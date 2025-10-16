# FinancialInsights

A real-time financial news sentiment analysis and stock trend correlation engine showcasing modern data engineering and ML engineering practices.

## Overview

The goal is to build a streaming data pipeline that ingests real-time financial news articles and stock price data, performs sentiment analysis on the news articles, and correlates the sentiment with stock price movements. The processed data is then stored in a MySQL database and made accessible via a FastAPI web service for visualization and further analysis.
In addition I want to use Toto-Open-Base-1.0 for time series forecasting of stock prices based on historical data and sentiment trends.

This is a work in progress project for learning and demonstrating skills in data engineering, machine learning engineering, and modern data stack technologies.

## Tech Stack

- **Streaming**: Apache Kafka for real-time data ingestion
- **Database**: MySQL for historical data storage
- **API**: FastAPI for data access and visualization
- **Orchestration**: Docker Compose for containerized deployment

## Project Structure
```
FinancialInsights/ 
├── config/ # Configuration files 
├── data/examples/ # Sample datasets (news.csv, prices.csv) 
├── db/ # Database initialization scripts 
├── kafka/ # Kafka topic setup scripts 
├── pipelines/ # Data pipeline components 
│ ├── producers/ # Kafka producers for news and prices 
│ └── ingestor_consumer.py # Kafka consumer 
├── services/api/ # FastAPI service 
└── docker-compose.yml # Container orchestration
```

## Getting Started

### Prerequisites

- Docker
- Python 3.12
- Make (optional, for using Makefile commands)
- [uv for dependency management](https://docs.astral.sh/uv/getting-started/installation/)

1. Clone the repository:
    ```bash
    git clone https://github.com/phucdev/FinancialInsights.git
    cd FinancialInsights
    ```
2. To install the dependencies, either use `make install` or do it manually with `uv`:
   ```bash
   uv venv && . .venv/bin/activate && uv sync --frozen
   ```
3. Copy the .env.example to .env and adjust configurations as needed:
   ```bash
   cp .env.example .env
   ```
4. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```
   In addition to starting Kafka, MySQL, the API server this will also run a helper that creates the news and prices topics.
5. Run the data producers to start sending synthetic data to Kafka:
   ```bash
   python pipelines/producers/news_producer.py
   ```
   And in another terminal run the consumer:
   ```bash
   python pipelines/ingestor_consumer.py
   ```

## Progress

### Phase 1 (Completed)
- ✅ Project structure setup
- ✅ Kafka broker configuration
- ✅ News producers with synthetically generated data
- ✅ Consumer for data ingestion

### Phase 2 (In Progress)
- 🔄 Producer/consumer refinement
- 🔄 MySQL integration for historical data storage
- 🔄 Data processing and transformation pipelines

### Phase 3 (Planned)
- ⏳ Sentiment analysis implementation
- ⏳ Stock trend correlation engine
- ⏳ Real-time analytics dashboard
- ⏳ API endpoints for data access

Contact
GitHub: [@phucdev](https://github.com/phucdev)