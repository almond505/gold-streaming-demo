import pandas as pd
from kafka import KafkaProducer
from time import sleep
import json
import yfinance as yf
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from gold_streaming_demo.config import KafkaConfig, GoldPriceConfig
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line %(lineno)d'
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True

def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals gracefully.
    
    Args:
        signum (int): Signal number
        frame (Any): Current stack frame
    """
    global running
    logger.info("Received shutdown signal. Cleaning up...")
    running = False

def create_producer(config: KafkaConfig) -> KafkaProducer:
    """Create and return a Kafka producer with the given configuration.
    
    Args:
        config (KafkaConfig): Configuration object containing Kafka settings
        
    Returns:
        KafkaProducer: Configured Kafka producer instance
        
    Raises:
        Exception: If producer creation fails
    """
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
    """Fetch gold price data from Yahoo Finance.
    
    Args:
        config (GoldPriceConfig): Configuration object containing gold price settings
        
    Returns:
        pd.DataFrame: DataFrame containing gold price data with columns:
            - Datetime: Timestamp of the price
            - Open: Opening price
            - High: Highest price
            - Low: Lowest price
            - Close: Closing price
            - Volume: Trading volume
            
    Raises:
        Exception: If data fetching fails
    """
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

def produce_messages(producer: KafkaProducer, data: pd.DataFrame, topic: str) -> None:
    """Produce messages to Kafka topic.
    
    Args:
        producer (KafkaProducer): Configured Kafka producer instance
        data (pd.DataFrame): DataFrame containing gold price data to send
        topic (str): Name of the Kafka topic to produce to
        
    Raises:
        Exception: If message production fails
    """
    try:
        if data.empty:
            logger.warning("No data to produce")
            return
            
        for _, row in data.iterrows():
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

def run_producer(fetch_interval: int = 60) -> None:
    """Main function to run the producer continuously.
    
    This function:
    1. Sets up signal handlers for graceful shutdown
    2. Creates a Kafka producer
    3. Continuously fetches gold price data
    4. Produces messages to Kafka topic
    5. Handles errors and cleanup
    
    Args:
        fetch_interval (int, optional): Time in seconds between data fetches. Defaults to 60.
        
    Raises:
        Exception: If producer setup or execution fails
    """
    global running
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        kafka_config = KafkaConfig()
        gold_config = GoldPriceConfig()
        
        producer = create_producer(kafka_config)
        logger.info(f"Starting continuous data fetching with {fetch_interval}s interval")
        
        while running:
            try:
                gold_data = fetch_gold_data(gold_config)
                if not gold_data.empty:
                    produce_messages(producer, gold_data, kafka_config.topic_name)
                else:
                    logger.warning("No data to process in this iteration")
                
                # Simple sleep with running flag check
                if running:
                    sleep(fetch_interval)
                    
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                if running:
                    sleep(5)  # Wait a bit before retrying on error
                
    except Exception as e:
        logger.error(f"Producer failed: {str(e)}")
        raise
    finally:
        if 'producer' in locals():
            producer.close()
            logger.info("Producer closed")

# Add this to make the file executable as a standalone script
if __name__ == "__main__":
    run_producer()
