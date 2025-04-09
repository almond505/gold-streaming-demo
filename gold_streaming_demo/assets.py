from dagster import asset, Definitions, AssetExecutionContext
import subprocess
import logging
import sys
from pathlib import Path
from .kafka_utils.producer import main as run_producer_main
from .kafka_utils.consumer import main as run_consumer_main
from .kafka_utils.start_kafka import start_kafka

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asset
def start_kafka_server(context: AssetExecutionContext):
    """Start Kafka and Zookeeper servers."""
    try:
        logger.info("Starting Kafka & Zookeeper...")
        success = start_kafka()
        if not success:
            raise RuntimeError("Failed to start Kafka server")
        logger.info("Kafka & Zookeeper started successfully.")
    except Exception as e:
        logger.error(f"Unexpected error starting Kafka: {str(e)}")
        raise

@asset(deps=[start_kafka_server])
def run_producer(context: AssetExecutionContext):
    """Run the gold price producer."""
    try:
        logger.info("Starting gold price producer...")
        run_producer_main()
        logger.info("Gold price producer completed successfully.")
    except Exception as e:
        logger.error(f"Producer failed: {str(e)}")
        raise

@asset(deps=[run_producer])
def run_consumer(context: AssetExecutionContext):
    """Run the gold price consumer."""
    try:
        logger.info("Starting gold price consumer...")
        run_consumer_main()
        logger.info("Gold price consumer completed successfully.")
    except Exception as e:
        logger.error(f"Consumer failed: {str(e)}")
        raise

defs = Definitions(
    assets=[start_kafka_server, run_producer, run_consumer]
)
