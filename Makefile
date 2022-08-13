TAG := $(shell git describe --tags)
NAME := "danops/splinter-sniper"

.PHONEY all
all: build run

build:
	docker build -t $(NAME):$(TAG) .

.PHONEY: push
push:
	docker push $(NAME):$(TAG)

.PHONEY: run
run:
	docker run --rm -e HIVE_USERNAME -e HIVE_ACTIVE_KEY $(NAME):$(TAG)
