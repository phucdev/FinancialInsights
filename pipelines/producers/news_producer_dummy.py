# Stream synthetic news.csv data to Kafka topic "news.raw" (JSON)
import datetime
import json
import os
import random
import uuid

from confluent_kafka import Producer
from dotenv import find_dotenv, load_dotenv

NEWS_TEMPLATES = {
    "AAPL": {
        "positive": [
            {
                "title": "Apple Posts Record Earnings, Driven by Services and New iPhone Sales",
                "body": "Apple Inc. announced its strongest quarter ever, "
                "crediting a surge in subscription services and robust demand "
                "for the latest iPhone model. Analysts across the board "
                "have raised their price targets. ",
            },
            {
                "title": "New Patent Filing Suggests Breakthrough in Apple Car Battery Technology",
                "body": "A recently published patent details a novel solid-state "
                "battery architecture that could drastically increase range "
                "and efficiency for future Apple Car projects, sparking investor optimism.",
            },
        ],
        "neutral": [
            {
                "title": "Apple Prepares for WWDC, Focuses on Software Updates",
                "body": "The company is gearing up for its annual Worldwide Developers Conference, "
                "expected to showcase iOS and macOS updates, with no major hardware "
                "reveals anticipated this cycle.",
            },
            {
                "title": "Apple Acquires Small AI Firm for Undisclosed Sum",
                "body": "Apple has completed the acquisition of 'SynapseAI,' a small, "
                "specialized firm focusing on edge computing. "
                "The financial details of the acquisition remain confidential.",
            },
        ],
        "negative": [
            {
                "title": "Apple Stock Tumbles on Concerns Over European Regulatory Fines",
                "body": "The stock dropped nearly 3% following reports that the EU is "
                "preparing a significant fine related to alleged anti-competitive "
                "behavior in its digital payment services market.",
            },
            {
                "title": "Supply Chain Snags Force Delay of Key Apple Product Launch",
                "body": "Component shortages, particularly in advanced display drivers, "
                "have led Apple to push back the launch of its highly anticipated "
                "VR headset by one quarter.",
            },
        ],
    },
    "MSFT": {
        "positive": [
            {
                "title": "Microsoft's Cloud Revenue Soars Past Expectations, Azure Leads Growth",
                "body": "Strong growth in Microsoft Azure propelled the company to beat "
                "revenue forecasts, underscoring its dominance in the enterprise "
                "cloud computing space. [Image of cloud computing infrastructure]",
            },
        ],
        "neutral": [
            {
                "title": "Microsoft Announces Global Reorganization to Streamline Operations",
                "body": "The company detailed plans for a major internal restructuring aimed at "
                "improving cross-department collaboration, with no immediate impact on "
                "its financial outlook.",
            },
        ],
        "negative": [
            {
                "title": "Major Security Breach Hits Microsoft Exchange Servers Globally",
                "body": "A critical vulnerability was exploited in Microsoft Exchange, "
                "leading to data exposure "
                "for several large corporate clients. The company is rushing to deploy a patch.",
            },
        ],
    },
    # Default templates for any other ticker
    "DEFAULT": {
        "positive": [
            {
                "title": "Q3 Report Shows Strong Momentum; Earnings Per Share Beats Forecast",
                "body": "The company's recent quarterly report highlights robust o"
                "perational efficiency and "
                "better-than-expected earnings per share, reassuring investors.",
            },
        ],
        "neutral": [
            {
                "title": "Company Holds Annual Shareholders Meeting; Maintains 2024 Guidance",
                "body": "In its yearly meeting, management confirmed that the company "
                "is on track to meet its "
                "financial targets for the current fiscal year. "
                "No major announcements were made.",
            },
        ],
        "negative": [
            {
                "title": "CEO Resigns Abruptly Amidst Internal Restructuring",
                "body": "Shares fell after the unexpected announcement that the "
                "long-standing CEO has stepped down, "
                "citing 'personal reasons' for the immediate departure.",
            },
        ],
    },
}

# Define score ranges for random generation
SCORE_RANGES = {
    "positive": (0.6, 1.0),
    "neutral": (0.4, 0.6),
    "negative": (0.0, 0.4),
}


def get_date_time():
    now_utc = datetime.datetime.now(datetime.UTC)
    return now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def sample_ticker():
    return random.sample(["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"], 1)[0]


def sample_source():
    return random.sample(["Reuters", "Bloomberg", "CNBC", "WSJ", "NYT", "TechCrunch"], 1)[0]


def sample_article(ticker_name):
    """
    Generate a sample news article for the given ticker.
    :param ticker_name: Stock ticker symbol
    :return: Dict with title, body, sent_label (sentiment label) and sent_score (sentiment score)
    """
    # 1. Determine which set of templates to use (specific or default)
    templates = NEWS_TEMPLATES.get(ticker_name, NEWS_TEMPLATES["DEFAULT"])

    # 2. Randomly select a sentiment
    sentiment_label = random.choice(list(templates.keys()))

    # 3. Select a random article from the chosen sentiment group
    articles = templates[sentiment_label]
    article_data = random.choice(articles)

    # 4. Generate a random score within the sentiment's defined range
    min_score, max_score = SCORE_RANGES[sentiment_label]
    sentiment_score = round(random.uniform(min_score, max_score), 4)

    return {
        "title": article_data["title"],
        "body": article_data["body"],
        "sent_label": sentiment_label,
        "sent_score": sentiment_score,
    }


def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered {msg.value().decode('utf-8')}")
        print(f"    to topic {msg.topic()} partition [{msg.partition()}] at offset {msg.offset()}")


# Set up our producer
load_dotenv(find_dotenv())
producer_config = {
    "bootstrap.servers": os.getenv("KAFKA_BROKER_HOST", "localhost:9092"),
}

producer = Producer(producer_config)

# Example data
ticker = sample_ticker()
article = sample_article(ticker)
message = {
    "id": str(uuid.uuid4()),
    "ts": get_date_time(),
    "ticker": ticker,
    "source": sample_source(),
    "title": article["title"],
    "body": article["body"],
    "sent_label": article["sent_label"],
    "sent_score": article["sent_score"],
}

message_bytes = json.dumps(message).encode("utf-8")
# This buffers messages and sends them in batches
producer.produce(topic="news.raw", value=message_bytes, callback=delivery_report)
producer.flush()  # Ensure all messages are sent before exiting
