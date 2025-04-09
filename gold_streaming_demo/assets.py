from dagster import asset, Definitions, AssetExecutionContext
import subprocess
import logging
from pathlib import Path
from gold_streaming_demo.kafka_utils.producer import main as run_producer_main
from gold_streaming_demo.kafka_utils.consumer import main as run_consumer_main

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
        script_path = Path("./scripts/kafka_start.sh")
        if not script_path.exists():
            raise FileNotFoundError(f"Kafka start script not found at {script_path}")
        
        result = subprocess.run(
            [str(script_path)],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(result.stdout)
        logger.info("Kafka & Zookeeper started successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Kafka: {e.stderr}")
        raise
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
