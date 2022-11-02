// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <iostream>
#include <string>

#include "seal/seal.h"
#include "sq_helper_functions.h"
#include "sq_types.h"
#include "sqclient.h"
#include "sqserver.h"
#include "timer.h"

int main() {
  SQClient sq_client;
  std::cout
      << "Initialize SEAL BFV scheme with default parameters[Y(default)|N]:";
  std::string interactive_init;
  std::getline(std::cin, interactive_init);

  // Here we initialize the client's SEAL context with desired poly modulus,
  // plain modulus, and database key length parameters.
  if (interactive_init == "" || interactive_init == "Y") {
    sq_client.initializeSealContext(std::pow(2, 13), 17);
  } else {
    sq_client.initializeSealContextInteractive();
  }
  /** Print the seal context and key length parameters which will be used to
   * initialize the server
   *
   */
  std::cout << "SEAL BFV context initialized with following parameters"
            << std::endl;
  std::cout << "Polymodulus degree: "
            << sq_client.sealParams().poly_modulus_degree() << std::endl;
  std::cout << "Plain modulus: "
            << sq_client.sealParams().plain_modulus().value() << std::endl;
  std::cout << "Key length: " << sq_client.keyLength() << std::endl;

  // Here we create the secure query server object. Note that the server never
  // gets access to the private key, only the context parameters and the public
  // key. The keylength is also passed.
  SQServer sq_server;
  sq_server.createSealContextFromParameters(sq_client.sealParams());
  sq_server.setKeyLength(sq_client.keyLength());
  sq_server.setPublicKey(*sq_client.publicKey());

  std::cout << "Input file to use for database or press enter to use "
               "default[us_state_capitals.csv]:";
  std::string database_file;
  std::getline(std::cin, database_file);
  if (database_file == "") {
    database_file = "us_state_capitals.csv";
  }
  std::vector<DatabaseEntry> unencrypted_database;
  try {  // Populate the database.
    unencrypted_database = sq::createDatabaseFromCSVFile(database_file);
  } catch (std::runtime_error& e) {
    std::cerr << "\n" << e.what() << std::endl;
    exit(1);
  }
  std::cout << "Number of database entries: " << unencrypted_database.size()
            << std::endl;
  std::cout << "Encrypting database entries into Ciphertexts" << std::endl;

  /** Here we create the encrypted database consisting of
   * (std::vector<Ciphertext>,Ciphertext) key,value pairs. For this example we
   * assume the client owns the database, so encrypts it then passes it to the
   * server. It is also possible for the server to own the database in which
   * case it would create the database and then encrypt it on its end using the
   * public key provided by the client.
   */
  std::vector<EncryptedDatabaseEntry> encrypted_database = sq::encryptDatabase(
      unencrypted_database, sq_client.encryptor(),
      sq_client.sealParams().poly_modulus_degree(), sq_client.keyLength());
  sq_server.setEncryptedDatabase(encrypted_database);

  std::cout << "Input key value to use for database query:";
  std::string value;
  std::getline(std::cin, value);
  std::vector<seal::Ciphertext> query_vec_ct =
      sq_client.encodeStringQuery(value);

  std::cout << "Querying database for key: " << value << std::endl;
  intel::Common::Timer query_timer;
  query_timer.start();
  /** This command queries the database for an entry who's key matches the
   * query_vec_ct.
   *
   */
  seal::Ciphertext database_lookup_result =
      sq_server.queryDatabaseForMatchingEntry(query_vec_ct,
                                              *sq_client.relinKeys());
  query_timer.stop();
  std::string database_string =
      sq_client.decodeToString(database_lookup_result);
  std::cout << "Decoded database entry: " << database_string << std::endl
            << std::endl;

  std::cout << "Total query elapsed time(seconds): "
            << query_timer.elapsedSeconds() << std::endl;
  std::cout << "Records searched per second: "
            << unencrypted_database.size() / query_timer.elapsedSeconds()
            << std::endl;

  return 0;
}
