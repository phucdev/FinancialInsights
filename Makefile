SHELL := /bin/bash

.PHONY: up down kafka-topics install run-producers run-consumer api

install:
	uv venv && . .venv/bin/activate && uv sync --frozen

up:
	@cp -n .env.example .env || true
	docker compose --env-file .env up -d --build
	@echo "MySQL: localhost:3306 | Kafka: localhost:9092 | API: http://localhost:8000/docs"

down:
	docker compose down -v

kafka-topics:
	docker compose run --rm kafka-setup

run-producers:
	. .venv/bin/activate && \
	uv run python pipelines/producers/news_producer_dummy.py & \
	uv run python pipelines/producers/price_producer_dummy.py

run-consumer:
	. .venv/bin/activate && \
	uv run python pipelines/ingestor_consumer.py

api:
	docker compose up -d api
	@echo "API: http://localhost:8000/docs"
