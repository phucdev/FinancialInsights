import argparse
import os

from alpha_vantage.alphaintelligence import AlphaIntelligence
from alpha_vantage.timeseries import TimeSeries
from dotenv import find_dotenv, load_dotenv

DAILY_COLUMN_MAP = {
    "1. open": "open",
    "2. high": "high",
    "3. low": "low",
    "4. close": "close",
    "5. volume": "volume",
}

TABLE_PRICES = "prices_daily"
TABLE_NEWS = "news_daily"  # aggregated per ticker per date (suggested)


class Config:
    """Holds runtime configuration parsed from env/CLI."""

    def __init__(
        self,
        api_key: str,
        tickers: list[str],
        max_days: int,
        mysql_uri: str,
        store_headlines: bool = True,
        aggregate_news: bool = True,
        dry_run: bool = False,
    ):
        """
        The configuration for the daily API ingestion pipeline.
        :param api_key: The Alpha Vantage API key.
        :param tickers: The list of stock tickers to fetch data for.
        :param max_days: The maximum number of days of data to fetch.
        :param mysql_uri: The MySQL connection URI.
        :param store_headlines: Whether to store individual news headlines.
        :param aggregate_news: Whether to aggregate news data.
        :param dry_run: Whether to run in dry-run mode (no DB writes).
        """
        self.api_key = api_key
        self.tickers = [t.strip().upper() for t in tickers if t.strip()]
        self.max_days = max_days
        self.mysql_uri = mysql_uri
        self.store_headlines = store_headlines
        self.aggregate_news = aggregate_news
        self.dry_run = dry_run


def parse_args() -> Config:
    """Parse command-line arguments and environment variables into a Config object."""
    parser = argparse.ArgumentParser(description="Daily API Ingestion Pipeline Configuration")
    parser.add_argument("--api-key", type=str, required=False, help="Alpha Vantage API key")
    parser.add_argument(
        "--tickers", type=str, required=True, help="Comma-separated list of stock tickers"
    )
    parser.add_argument(
        "--max-days", type=int, default=30, help="Maximum number of days of data to fetch"
    )
    parser.add_argument("--mysql-uri", type=str, required=False, help="MySQL connection URI")
    parser.add_argument(
        "--store-headlines", action="store_true", help="Store individual news headlines"
    )
    parser.add_argument("--aggregate-news", action="store_true", help="Aggregate news data")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no DB writes)")

    args = parser.parse_args()

    load_dotenv(find_dotenv())
    api_key = args.api_key
    if api_key is None:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if api_key is None:
            raise ValueError(
                "API key must be provided via --api-key or ALPHAVANTAGE_API_KEY env variable"
            )
    tickers = args.tickers.split(",")
    if not args.mysql_uri:
        # Build MySQL URI from env variables
        host = os.getenv("MYSQL_HOST", "localhost")
        port = int(os.getenv("MYSQL_PORT", "3306"))
        db = os.getenv("MYSQL_DB", os.getenv("MYSQL_DATABASE", "financial_insights"))
        user = os.getenv("MYSQL_USER", "app")
        pwd = os.getenv("MYSQL_PASSWORD", "app_pw")
        mysql_uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"
    else:
        mysql_uri = args.mysql_uri

    return Config(
        api_key=api_key,
        tickers=tickers,
        max_days=args.max_days,
        mysql_uri=mysql_uri,
        store_headlines=args.store_headlines,
        aggregate_news=args.aggregate_news,
        dry_run=args.dry_run,
    )


load_dotenv(find_dotenv())
ts = TimeSeries(key=os.getenv("ALPHAVANTAGE_API_KEY"), output_format="pandas")
ai = AlphaIntelligence(key=os.getenv("ALPHAVANTAGE_API_KEY"))

timer_series_stock_data, metadata = ts.get_daily("GOOGL")
news_data = ai.get_news_sentiment("GOOGL")[0]
