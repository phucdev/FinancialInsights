CREATE DATABASE IF NOT EXISTS market;
USE market;

CREATE TABLE IF NOT EXISTS prices_minute (
  ticker VARCHAR(10),
  ts DATETIME,
  close DOUBLE,
  volume BIGINT,
  PRIMARY KEY (ticker, ts)
);

CREATE TABLE IF NOT EXISTS news_sentiment (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ticker VARCHAR(10),
  ts DATETIME,
  source VARCHAR(64),
  title VARCHAR(512),
  sent_label ENUM('neg','neu','pos') NULL,
  sent_score DOUBLE,
  UNIQUE KEY uniq_news (ticker, ts, title(128))
);

CREATE TABLE IF NOT EXISTS joined_minute (
  ticker VARCHAR(10),
  ts DATETIME,
  sent_mean_1m DOUBLE,
  sent_count INT,
  ret_1m DOUBLE,
  price DOUBLE,
  volume BIGINT,
  PRIMARY KEY (ticker, ts)
);
