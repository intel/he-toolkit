/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include "data_record.h"

#include <kafka/AdminClient.h>
#include <kafka/KafkaConsumer.h>
#include <kafka/KafkaProducer.h>

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <map>
#include <memory>
#include <regex>
#include <string>
#include <utility>
#include <vector>

#include <nlohmann/json.hpp>
using json = nlohmann::json;
using kConsumer = kafka::clients::KafkaConsumer;
using kProducer = kafka::clients::KafkaProducer;
namespace fs = std::filesystem;

// Interface for Data Connection
struct DataConn {
  virtual void open() = 0;
  virtual void close() = 0;
  virtual std::unique_ptr<DataRecord> read() const = 0;
  virtual void write(DataRecord& data) const = 0;
  virtual std::unique_ptr<DataRecord> createDataRecord(
      const Metadata& metadata = {}) const = 0;
  virtual ~DataConn() = default;
};

// Interface for Data Connection Configuration
struct DataConnConfig {
  virtual ~DataConnConfig() = default;
};

class KafkaConfig : public DataConnConfig {
 private:
  std::string directory_;
  std::string topic_;
  std::string broker_;
  std::string mode_;

 public:
  KafkaConfig(const json& json_config) {
    json_config.at("directory").get_to(directory_);
    json_config.at("broker").get_to(broker_);

    if (json_config.at("io") == "read") {
      mode_ = "read";
      // Kafka topic is dynamic for outgoing messages
      json_config.at("topic").get_to(topic_);
    } else if (json_config.at("io") == "write") {
      mode_ = "write";
    } else {
      std::ostringstream msg;
      msg << "Invalid io argument '" << json_config.at("io").get<std::string>()
          << "'";
      throw std::runtime_error(msg.str());
    }
  }

  std::string directory() const { return directory_; }
  std::string topic() const { return topic_; }
  std::string broker() const { return broker_; }
  std::string mode() const { return mode_; }
};

class FileSysConfig : public DataConnConfig {
 private:
  std::string directory_;
  std::string extension_;
  std::string meta_ext_;
  std::string mode_;

 public:
  FileSysConfig(const json& json_config) {
    json_config.at("directory").get_to(directory_);
    // These are optional
    if (json_config.contains("ext")) {
      json_config.at("ext").get_to(extension_);
    }
    if (json_config.contains("meta_ext")) {
      json_config.at("meta_ext").get_to(meta_ext_);
    }

    // Use correct stream modes
    if (json_config.at("io") == "read") {
      mode_ = "read";
    } else if (json_config.at("io") == "write") {
      mode_ = "write";
    } else {
      std::ostringstream msg;
      msg << "Invalid io argument '" << json_config.at("io").get<std::string>()
          << "'";
      throw std::runtime_error(msg.str());
    }
  }

  std::string directory() const { return directory_; }
  std::string extension() const { return extension_; }
  std::string meta_ext() const { return meta_ext_; }
  std::string mode() const { return mode_; }
};

// Concrete class implementing access of a Kafka connection
class KafkaConn : public DataConn {
 private:
  KafkaConfig config_;
  std::unique_ptr<kConsumer> consumer_ptr_;
  std::unique_ptr<kProducer> producer_ptr_;

  template <typename T>
  std::string find(const std::string& key, const T& record) const {
    for (const auto& header : record.headers()) {
      // Assume the keys are unique
      if (key == header.key) {
        return header.value.toString();
      }
    }
    throw std::runtime_error("Key '" + key + "' not found.");
  }

  std::string fixNewline(const std::string& s) const {
    return std::regex_replace(s, std::regex(R"(\[0x0a\])"), "\n");
  }

  bool isTopicCreated(kafka::clients::AdminClient& adminClient,
                      const std::string& topic) {
    auto setTopics = adminClient.listTopics().topics;
    return setTopics.find(topic) != setTopics.end();
  }

 public:
  KafkaConn(const KafkaConfig& config) : config_(config) { open(); }
  KafkaConn(const json& config) : KafkaConn(KafkaConfig(config)) {}
  KafkaConn() = delete;

  void open() override {
    if (config_.mode() == "read") {
      auto kafka_topic = config_.topic();
      std::cout << "Subscribing to kafka topic: " << kafka_topic << std::endl;

      kafka::Properties admin_props({
          {"bootstrap.servers", config_.broker()},
      });
      kafka::clients::AdminClient adminClient(admin_props);
      while (false == isTopicCreated(adminClient, kafka_topic)) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
      }

      kafka::Properties consumer_props(
          {{"bootstrap.servers", config_.broker()},
           {"enable.auto.commit", "true"},
           {"group.id", "TestGroup"},
           {"auto.offset.reset", "smallest"},
           {"max.poll.records", "1"},
           {"receive.message.max.bytes", "157286400"}});
      consumer_ptr_ = std::make_unique<kConsumer>(consumer_props);
      consumer_ptr_->subscribe({config_.topic()});
      return;
    }

    if (config_.mode() == "write") {
      kafka::Properties producer_props({
          {"bootstrap.servers", config_.broker()},
          {"enable.idempotence", "true"},
          {"message.max.bytes", "157286400"},
      });
      producer_ptr_ = std::make_unique<kProducer>(producer_props);
      return;
    }

    std::ostringstream msg;
    msg << "Unknown file mode '" << config_.mode() << "'";
    throw std::runtime_error(msg.str());
  }

  void close() override {
    if (config_.mode() == "read") {
      consumer_ptr_->unsubscribe();
      consumer_ptr_->close();
    }
    if (config_.mode() == "write") {
      producer_ptr_->close();
    }
  }

  std::unique_ptr<DataRecord> read() const override {
    auto records = consumer_ptr_->poll(std::chrono::milliseconds(1000));
    if (records.size() == 0) {
      // std::cout << "No record found.\n";
      return nullptr;
    }
    if (records.size() > 1) {
      throw std::runtime_error("More than one record detected.");
    }
    const auto& record = records.front();
    if (record.value().size() == 0) {
      return nullptr;
    }
    auto bank_id = find("BID", record);
    auto user_id = find("UID", record);
    auto job_id = find("JobID", record);
    std::string metafile = job_id + ".heql";
    fs::path metadata_filepath = fs::path(config_.directory()) / metafile;
    std::string datafilename = job_id + ".query";
    fs::path datafilepath = fs::path(config_.directory()) / datafilename;
    if (record.error()) {
      std::cerr << record.toString() << std::endl;
    } else {
      // Write Kafka record to disk
      std::ofstream metadata(metadata_filepath, std::ios::out);
      if (!metadata.is_open()) {
        std::ostringstream msg;
        msg << "Could not open file '" << metadata_filepath << "'";
        throw std::runtime_error(msg.str());
      }
      metadata << fixNewline(find("HEQL", record));

      std::ofstream datafile(datafilepath, std::ios::out | std::ios::binary);
      if (!datafile.is_open()) {
        std::ostringstream msg;
        msg << "Could not open file '" << datafilepath << "'";
        throw std::runtime_error(msg.str());
      }
      const auto& value = record.value();
      datafile.write(reinterpret_cast<const char*>(value.data()), value.size());
    }
    // Create out topic
    std::ostringstream out_topic;
    out_topic << bank_id << "." << user_id << "." << job_id;

    // return std::make_unique<FileRecord>(
    // datafilepath, config_.mode(), Metadata{{"out-topic", out_topic.str()}},
    // metadata_filepath);

    // Create kakfa record and write data to record
    auto kafka_record = std::make_unique<KafkaRecord>(
        Metadata{{"out-topic", out_topic.str()},
                 {"heql", fixNewline(find("HEQL", record))}});
    kafka_record->write(
        const_cast<char*>(reinterpret_cast<const char*>(record.value().data())),
        record.value().size());
    return kafka_record;
  }

  void write(DataRecord& data) const override {
    // Create record
    kafka::Value value(data.data(), data.size());
    auto topic_name = data.metadata("out-topic");
    auto record = kafka::clients::producer::ProducerRecord(
        topic_name,
        /*partition=*/0, /*kafka::Key*/ kafka::NullKey, /*kafka::Value*/ value);

    // Send to Kafka
    producer_ptr_->send(
        record,
        // The delivery report handler
        [](const kafka::clients::producer::RecordMetadata& metadata,
           const kafka::Error& error) {
          if (!error) {
            std::cout << "% Message delivered: " << metadata.toString()
                      << std::endl;
          } else {
            std::cerr << "% Message delivery failed: " << error.message()
                      << std::endl;
          }
        },
        // The memory block given by record.value() would be copied
        kProducer::SendOption::ToCopyRecordValue);
  }

  std::unique_ptr<DataRecord> createDataRecord(
      const Metadata& metadata = {}) const override {
    return std::make_unique<KafkaRecord>(metadata);
  }

  ~KafkaConn() { close(); }
};

// Concrete class implementing access of a local file system
class FileSys : public DataConn {
 private:
  FileSysConfig config_;
  mutable long current_entry_ = 0;
  std::vector<std::pair<std::string, std::string>> filenames_;

  void openForRead() {
    auto it = fs::directory_iterator(config_.directory());
    std::vector<fs::directory_entry> filenames;
    std::copy_if(it, {}, std::back_inserter(filenames),
                 [extension = config_.extension(),
                  meta_ext = config_.meta_ext()](const auto& filepath) {
                   return filepath.is_regular_file() &&
                          (extension == filepath.path().extension() ||
                           meta_ext == filepath.path().extension());
                 });
    std::sort(filenames.begin(), filenames.end());

    for (long i = 0; i < filenames.size() - 1; i += 2) {
      const auto& first_path = filenames[i].path();
      const auto& second_path = filenames[i + 1].path();
      if (first_path.stem() != second_path.stem()) {
        i--;  // Loop incrementor only adds 1
        std::cerr << "No match found.\n";
        continue;
      }
      if (first_path.extension() == config_.meta_ext()) {
        filenames_.emplace_back(second_path, first_path);
        continue;
      }
      filenames_.emplace_back(first_path, second_path);
    }
  }

  // This may do something in the future.
  void openForWrite() {}

 public:
  // Factory method
  FileSys(const FileSysConfig& config) : config_(config) { open(); }
  FileSys(const json& config) : FileSys(FileSysConfig(config)) {}
  FileSys() = delete;

  void open() override {
    if (config_.mode() == "read") {
      openForRead();
      return;
    }

    if (config_.mode() == "write") {
      openForWrite();
      return;
    }

    std::ostringstream msg;
    msg << "Unknown file mode '" << config_.mode() << "'";
    throw std::runtime_error(msg.str());
  }

  void close() override {}  // This is supposed to do nothing

  std::unique_ptr<DataRecord> read() const override {
    if (current_entry_ >= filenames_.size()) {
      return nullptr;
    }
    auto [filename, metadata_filename] = filenames_.at(current_entry_++);
    return std::make_unique<FileRecord>(filename, config_.mode(),
                                        metadata_filename);
  }

  // Currently this will do nothing because the file will already exist for PSI
  // but the behaviour could change in the future.
  void write(DataRecord& data) const override {}

  std::unique_ptr<DataRecord> createDataRecord(
      const Metadata& metadata = {}) const override {
    return std::make_unique<FileRecord>(config_.directory(), config_.mode());
  }
};

enum class Type { FILESYS, KAFKA };

std::string typeToString(const Type& type) {
  switch (type) {
    case Type::FILESYS:
      return "filesys";
    case Type::KAFKA:
      return "kafka";
    default:
      throw std::logic_error("Unknown type.");
  }
}

static std::unique_ptr<DataConn> makeDataConn(const Type& conn_type,
                                              const json& config) {
  switch (conn_type) {
    case Type::FILESYS:
      return std::make_unique<FileSys>(config);
    case Type::KAFKA:
      return std::make_unique<KafkaConn>(config);
    default:
      std::ostringstream msg;
      msg << "Invalid data connection '" << typeToString(conn_type) << "'";
      throw std::runtime_error(msg.str());
  }
}
