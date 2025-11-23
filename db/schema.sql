CREATE DATABASE IF NOT EXISTS market;
USE market;

CREATE TABLE IF NOT EXISTS prices_daily (
    ticker  VARCHAR(10)     NOT NULL,
    date    DATE            NOT NULL,
    open    DECIMAL(18,6)   NOT NULL,
    high    DECIMAL(18,6)   NOT NULL,
    low     DECIMAL(18,6)   NOT NULL,
    close   DECIMAL(18,6)   NOT NULL,
    volume  BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (ticker, date),
    INDEX idx_prices_daily_date (date)          -- for faster date-based queries, e.g. WHERE date='2025-01-01'
);

CREATE TABLE IF NOT EXISTS news_sentiment (
    id             VARCHAR(128)  NOT NULL,  -- stable hash of url|ticker|date
    article_id     VARCHAR(128)  NOT NULL,  -- hash of url (same article across tickers)
    ticker         VARCHAR(10)   NOT NULL,
    published_at   DATETIME      NOT NULL,
    date           DATE          NOT NULL,  -- convenience YYYY-MM-DD (UTC day)
    title          VARCHAR(512)  NULL,
    url            VARCHAR(512)  NULL,
    source         VARCHAR(64)   NULL,
    summary        TEXT          NULL,
    sent_score     DOUBLE        NOT NULL,  -- sentiment score in [-1, 1]
    sent_label     ENUM('neg','neu','pos') NOT NULL,
    raw            JSON          NULL,      -- optional: full
    PRIMARY KEY (id),
    UNIQUE KEY uq_news_article_ticker_date (article_id, ticker, date),  -- prevent duplicates
    INDEX idx_news_ticker_date (ticker, date),  -- for faster ticker-date based queries
    INDEX idx_news_published_at (published_at)  -- for faster time-based queries
    INDEX idx_news_article_id (article_id)
);
