export TAG := $(shell git describe --tags)
NAME := "danops/splinter-sniper"

.PHONEY: all
all: build run

build:
	docker build -t $(NAME):$(TAG) -t $(NAME):latest .

.PHONEY: push
push:
	docker push $(NAME):$(TAG) && docker push $(NAME):latest

.PHONEY: run
run:
	docker run --rm --mount type=bind,source=$(PWD)/logs,target=/usr/app/src/logs --mount type=bind,source=$(PWD)/config.json,target=/usr/app/src/config.json -e HIVE_USERNAME -e HIVE_ACTIVE_KEY -e TZ=Europe/Madrid $(NAME):$(TAG)

.PHONEY: up
up:
	docker-compose up -d

.PHONEY: down
down:
	docker-compose down

.PHONEY: run_otel
run_otel:
	docker run --rm -p 4317:4317 -p 4318:4318 \
    -v $(PWD)/otel-collector-config.yaml:/etc/otel-collector-config.yaml \
    otel/opentelemetry-collector:latest \
    --config=/etc/otel-collector-config.yaml
