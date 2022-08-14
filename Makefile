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
	docker run --rm --mount type=bind,source=$(PWD)/logs,target=/usr/app/src/logs --mount type=bind,source=$(PWD)/config.json,target=/usr/app/src/config.json -e HIVE_USERNAME -e HIVE_ACTIVE_KEY $(NAME):$(TAG)

.PHONEY: up
up:
	docker-compose up -d

.PHONEY: down
down:
	docker-compose down
