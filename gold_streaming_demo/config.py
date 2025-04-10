from dagster import Config
from typing import Optional
import os

class KafkaConfig(Config):
    """Configuration class for Kafka settings.
    
    Attributes:
        bootstrap_servers (str): Kafka broker addresses. Defaults to "localhost:9092".
        topic_name (str): Name of the Kafka topic. Defaults to "gold_price_stream".
        consumer_group (str): Consumer group ID. Defaults to "gold_price_group".
    """
    bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name: str = os.getenv("KAFKA_TOPIC_NAME", "gold_price_stream")
    consumer_group: str = os.getenv("KAFKA_CONSUMER_GROUP", "gold_price_group")

class GoldPriceConfig(Config):
    """Configuration class for gold price data settings.
    
    Attributes:
        ticker_symbol (str): Yahoo Finance ticker symbol for gold. Defaults to "GC=F".
        interval (str): Data interval. Defaults to "1m" (1 minute).
        period (str): Data period. Defaults to "1d" (1 day).
        timezone (str): Timezone for data. Defaults to "Asia/Bangkok".
    """
    ticker_symbol: str = "GC=F"
    interval: str = "1m"
    period: str = "1d"
    timezone: str = "Asia/Bangkok"

class S3Config(Config):
    """Configuration class for S3 settings.
    
    Attributes:
        bucket_name (str): S3 bucket name. Defaults to "kafka-gold-bucket".
        prefix (str): Prefix for S3 object keys. Defaults to "gold_price".
    """
    bucket_name: str = os.getenv("S3_BUCKET_NAME", "kafka-gold-bucket")
    prefix: str = os.getenv("S3_PREFIX", "gold_price") 