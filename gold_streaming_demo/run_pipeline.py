import subprocess
import logging
import time
from pathlib import Path
from gold_streaming_demo.kafka_utils.producer import run_producer
from gold_streaming_demo.kafka_utils.consumer import run_consumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_kafka_server():
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
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Kafka: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error starting Kafka: {str(e)}")
        return False

def run_gold_price_producer():
    """Run the gold price producer."""
    try:
        logger.info("Starting gold price producer...")
        run_producer()
        logger.info("Gold price producer completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Producer failed: {str(e)}")
        return False

def run_gold_price_consumer():
    """Run the gold price consumer."""
    try:
        logger.info("Starting gold price consumer...")
        run_consumer()
        logger.info("Gold price consumer completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Consumer failed: {str(e)}")
        return False

def main():
    """Main function to run the entire pipeline."""
    logger.info("Starting gold streaming pipeline...")
    
    # Step 1: Start Kafka server
    if not start_kafka_server():
        logger.error("Failed to start Kafka server. Exiting.")
        return
    
    # Give Kafka some time to fully start
    logger.info("Waiting for Kafka to initialize...")
    time.sleep(10)
    
    # Step 2: Run the producer
    if not run_gold_price_producer():
        logger.error("Failed to run producer. Exiting.")
        return
    
    # Step 3: Run the consumer
    if not run_gold_price_consumer():
        logger.error("Failed to run consumer. Exiting.")
        return
    
    logger.info("Gold streaming pipeline completed successfully.")

if __name__ == "__main__":
    main() 