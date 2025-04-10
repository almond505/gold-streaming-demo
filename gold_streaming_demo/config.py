from dagster import Config
from typing import Optional
import os

class KafkaConfig(Config):
    bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name: str = os.getenv("KAFKA_TOPIC_NAME", "gold_price_stream")
    consumer_group: str = os.getenv("KAFKA_CONSUMER_GROUP", "gold_price_group")

class GoldPriceConfig(Config):
    ticker_symbol: str = "GC=F"
    interval: str = "1m"
    period: str = "1d"
    timezone: str = "Asia/Bangkok"

class S3Config(Config):
    bucket_name: str = os.getenv("S3_BUCKET_NAME", "kafka-gold-bucket")
    prefix: str = os.getenv("S3_PREFIX", "gold_price") 