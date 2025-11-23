import argparse
import json
import os
import pandas as pd
from typing import List, Dict, Any, Tuple

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


def make_clients(api_key: str):
    """Create Alpha Vantage API clients."""
    ts_client = TimeSeries(key=api_key, output_format="pandas")
    ai_client = AlphaIntelligence(key=api_key)
    return ts_client, ai_client


def fetch_daily_df(ts_client: TimeSeries, ticker: str):
    """Fetch daily stock data for a given ticker."""
    data, metadata = ts_client.get_daily(ticker)
    data = data.rename(columns=DAILY_COLUMN_MAP)
    # data.index = data.index.tz_localize("US/Eastern")
    return data


def fetch_news_data_df(
        ai_client: AlphaIntelligence,
        tickers: str,
        topics=None,
        time_from=None,
        time_to=None,
        sort='LATEST',
        limit=50
):
    """Fetch news sentiment data for a given ticker/comma separated list of tickers."""
    news_data = ai_client.get_news_sentiment(
        tickers=tickers,
        topics=topics,
        time_from=time_from,
        time_to=time_to,
        sort=sort,
        limit=limit
    )[0]
    return news_data


def normalize_prices_df(df: pd.DataFrame, ticker: str, max_days: int) -> List[Dict[str, Any]]:
    """
    Convert the client DataFrame into list-of-dicts for prices_daily.
    """
    df = df.sort_index(ascending=False).head(max_days).copy()
    rename = {
        "1. open": "open",
        "2. high": "high",
        "3. low":  "low",
        "4. close": "close",
        "5. volume": "volume",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    rows: List[Dict[str, Any]] = []
    for idx, row in df.iterrows():
        d = idx.date().isoformat()
        rows.append({
            "ticker": ticker,
            "date": d,
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low":  float(row["low"]),
            "close": float(row["close"]),
            "volume": int(row["volume"]),
        })
    return rows


def normalize_news_df(
    df: pd.DataFrame,
    watchlist: List[str],
) -> List[Dict[str, Any]]:
    """
    Build row per article.
    """
    if df.empty:
        df = pd.DataFrame(columns=[
            "id", "article_id", "ticker", "published_at", "date", "title", "url", "source", "summary", "raw"
        ])
    else:
        def parse_tp(tp: str) -> tuple[pd.Timestamp, str]:
            date_iso = f"{tp[:4]}-{tp[4:6]}-{tp[6:8]}"
            ts = pd.to_datetime(tp, format="%Y%m%dT%H%M%S", errors="coerce")
            if pd.isna(ts):
                ts = pd.to_datetime(date_iso)  # midnight
            # keep tz-naive UTC for MySQL (or set tz and convert)
            return ts, date_iso

        parsed = df["time_published"].apply(parse_tp)
        df["published_at"] = parsed.apply(lambda x: x[0])
        df["date"] = parsed.apply(lambda x: x[1])

        df = df.dropna(subset=["date", "url"])
        # Ensure ticker_sentiment is a list, then explode
        df["ticker_sentiment"] = df["ticker_sentiment"].apply(lambda x: x if isinstance(x, list) else [])
        df = df.loc[df["ticker_sentiment"].map(len) > 0]

        # Explode to one row per mentioned ticker
        df_expl = df.explode("ticker_sentiment", ignore_index=True)
        df_expl["mentioned_ticker"] = df_expl["ticker_sentiment"].apply(
            lambda d: (d or {}).get("ticker", "").upper()
        )
        # Filter to watchlist
        wl = set([t.upper() for t in watchlist])
        df_expl = df_expl[df_expl["mentioned_ticker"].isin(wl)]

        # Extract ticker specific sentiment score and label
        df_expl["sentiment_score"] = df_expl["ticker_sentiment"].apply(
            lambda d: (d or {}).get("sentiment_score", 0.0)
        )
        df_expl["sentiment_label"] = df_expl["ticker_sentiment"].apply(
            lambda d: (d or {}).get("sentiment_label", "")
        )

        
    return df.to_dict(orient="records")


load_dotenv(find_dotenv())
ts = TimeSeries(key=os.getenv("ALPHAVANTAGE_API_KEY"), output_format="pandas")
ai = AlphaIntelligence(key=os.getenv("ALPHAVANTAGE_API_KEY"))

timer_series_stock_data, metadata = ts.get_daily("GOOGL")
news_data = ai.get_news_sentiment("GOOGL")[0]
