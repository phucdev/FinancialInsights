SHELL := /bin/bash

.PHONY: up down kafka-topics install run-producers run-consumer spark-stream api airflow

install:
	uv venv && . .venv/bin/activate && uv sync --frozen --extra spark --extra api

up:
	@cp -n .env.example .env || true
	docker compose --env-file .env up -d --build
	@echo "MySQL: localhost:3306 | Kafka: localhost:9092 | Airflow: http://localhost:8080 | API: http://localhost:8000/docs"

down:
	docker compose down -v

kafka-topics:
	docker compose run --rm kafka-setup

run-producers:
	. .venv/bin/activate && \
	uv run python pipelines/producers/news_producer_dummy.py & \
	uv run python pipelines/producers/price_producer_dummy.py

# ---- Choose ONE ingestion path below ----

# Path A: Python consumer
run-consumer:
	. .venv/bin/activate && \
	uv run python pipelines/ingestor_consumer.py

# Path B: Spark streaming (optional)
spark-stream:
	. .venv/bin/activate && \
	spark-submit --master local[*] \
	 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
	 pipelines/stream_join_spark.py

api:
	docker compose up -d api
	@echo "API: http://localhost:8000/docs"

airflow:
	docker compose up -d airflow
	@echo "Airflow: http://localhost:8080  (admin/admin)"
