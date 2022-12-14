.ONESHELL:

.PHONY: clean install tests start-local all

clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.log' -delete

start-local:
	. venv/bin/activate
	dotenv -f './deployment/dev/.env.dev' run python manage.py run -h 0.0.0.0

docker-create-network:
	docker network create --driver overlay --attachable my_net

docker-install:
	docker volume create postgres_data
	docker volume create storage_data
	docker volume create storage_keys

	mkdir ~/storage_1/
	mkdir ~/storage_1/storage_data
	mkdir ~/storage_1/storage_keys
	mkdir ~/storage_1/postgres_data

docker-create-database-volume:
	docker volume create postgres_data

docker-create-storage-volume:
	docker volume create storage_data

docker-create-storage-keys-volume:
	docker volume create storage_keys

docker-compose-start-dev:
	docker compose -f docker-compose.dev.yaml up -d --build

docker-compose-stop-dev:
	docker compose -f docker-compose.dev.yaml down


docker-compose-start-kafka-cluster:
	docker compose -f deployment/kafka-cluster/docker-compose.yaml up -d

docker-compose-stop-kafka-cluster:
	docker compose -f deployment/kafka-cluster/docker-compose.yaml down -v

# Run tests
test:
	. venv/bin/activate
	pytest

all: clean install test start-local
