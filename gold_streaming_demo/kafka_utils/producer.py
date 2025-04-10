import pandas as pd
from kafka import KafkaProducer
from time import sleep
import json
import yfinance as yf
import logging
from datetime import datetime
from gold_streaming_demo.config import KafkaConfig, GoldPriceConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line %(lineno)d'
)
logger = logging.getLogger(__name__)

def create_producer(config: KafkaConfig) -> KafkaProducer:
    """Create and return a Kafka producer with the given configuration."""
    try:
        logger.info(f"Creating Kafka producer with bootstrap servers: {config.bootstrap_servers}")
        return KafkaProducer(
            bootstrap_servers=config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {str(e)}")
        raise

def fetch_gold_data(config: GoldPriceConfig) -> pd.DataFrame:
    """Fetch gold price data from Yahoo Finance."""
    try:
        logger.info(f"Fetching gold data for {config.ticker_symbol}")
        gold_data = yf.download(
            config.ticker_symbol,
            interval=config.interval,
            period=config.period
        )
        gold_data.index = gold_data.index.tz_convert(config.timezone)
        gold_df_sorted = gold_data.sort_values(by='Datetime', ascending=False)
        # 1. Join MultiIndex levels into strings
        gold_df_sorted.columns = ['_'.join(map(str, col)).strip() for col in gold_df_sorted.columns]
        # 2. Optional: remove '_GC=F' from column names
        gold_df_sorted.columns = [col.replace('_GC=F', '') for col in gold_df_sorted.columns]
        df = gold_df_sorted.reset_index()
        return df
    except Exception as e:
        logger.error(f"Failed to fetch gold data: {str(e)}")
        raise

def produce_messages(producer: KafkaProducer, data: pd.DataFrame, topic: str):
    """Produce messages to Kafka topic."""
    try:
        for _, row in data.iterrows():
            # message = {
            #     'timestamp': datetime.now().isoformat(),
            #     'data': row.to_dict()
            # }
            message = row.to_dict()
            message['Datetime'] = message['Datetime'].isoformat()
            logger.info(f"Producing message: {message}")
            producer.send(topic, value=message)
            logger.info(f"Sent message: {message}")
        producer.flush()
        logger.info(f"Successfully produced messages to topic {topic}")
    except Exception as e:
        logger.error(f"Failed to produce messages: {str(e)}")
        raise e

def run_producer():
    """Main function to run the producer."""
    try:
        kafka_config = KafkaConfig()
        gold_config = GoldPriceConfig()
        
        producer = create_producer(kafka_config)
        gold_data = fetch_gold_data(gold_config)
        produce_messages(producer, gold_data, kafka_config.topic_name)
        
    except Exception as e:
        logger.error(f"Producer failed: {str(e)}")
        raise
    finally:
        if 'producer' in locals():
            producer.close()

# Add this to make the file executable as a standalone script
if __name__ == "__main__":
    run_producer()
