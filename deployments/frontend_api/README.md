# API and cluster
Source code for the API and cluster project.

# Requirements
The following section describes the requirements needed for each OS.

## Windows
- Docker 4.x
- Make (Check https://stackoverflow.com/questions/2532234/how-to-run-a-makefile-in-windows)

# Execution
Before executing the API or the kafka-cluster the following files must be updated.

| File | Variables | Description
|-----------|-----------|-----------|
| Dockerfile.dev | {USER} | The user name
| deployment/dev/.env.dev | {IP_DATABASE_SERVER} | Server IP Address that hosts the database
| deployment/dev/.env.dev | {IP_KAFKA_SERVER} | Server IP Address that hosts the kafka cluster
| deployment/dev/.env.dev | {USER} | The user name
| deployment/kafka-cluster/docker-compose.yaml | {SERVER_IP} | Server IP Address that hosts the kafka-cluster
| docker-compose.dev.yaml | {USER} | The user name
| fetcher/deployment/dev/.env.dev | {IP_DATABASE_SERVER} | Server IP Address that hosts the database
| fetcher/deployment/dev/.env.dev | {IP_KAFKA_SERVER} | Server IP Address that hosts the kafka cluster
| frontend/src/environments/environment.ts | {IP_API_SERVER} | Server IP Address that hosts the API

## Run kafka-cluster
Use the following instructions to run the kafka-cluster project.
1. ```mkdir repo```
2. ```cd repo```
3. ```git clone <the-repo>```
4. ```cd <the-repo>```
5. ```make docker-compose-start-kafka-cluster```
4. To stop the deployment use ```make docker-compose-stop-kafka-cluster```

## Run API
Prerequisite: install Intel HE-toolkit
1. ```mkdir repo```
2. ```cd ~/repo```
3. ```git clone https://github.com/intel/he-toolkit.git```
4. ```cd he-toolkit/```
5. ```pip install -r requirements.txt```
6. ```./hekit init --default-config```
7. ```source ~/.bashrc```
8. ```hekit docker-build```

Use the following instructions to run the API project.
1. ```cd ~/repo```
2. ```git clone <the-repo>```
3. ```cd <the-repo>```
4. ```make docker-install```
5. Copy config file (`.toml`) to `~/storage_1/storage_data/`
6. Copy public and private keys (`.pk` and `.sk`) to `~/storage_1/storage_keys/`
7. Copy database file (`.heql`) to `~/storage_1/postgres_data/`
8. Update `username` in `Dockerfile.dev` file
9. ```make docker-compose-start-dev```
10. To stop the deployment use ```make docker-compose-stop-dev```

# Development
Once the docker-compose environment is up, you can edit the project files and
the application will automatically refresh.
