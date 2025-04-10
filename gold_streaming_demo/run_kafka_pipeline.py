import subprocess
import logging
import time
import os
import sys
import multiprocessing
from pathlib import Path

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
        stop_path = Path("./scripts/kafka_stop.sh")
        
        if not script_path.exists():
            raise FileNotFoundError(f"Kafka start script not found at {script_path}")
        
        # Make script executable
        script_path.chmod(0o755)
        stop_path.chmod(0o755)
        
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

def run_producer_process():
    """Run the gold price producer in a separate process."""
    try:
        logger.info("Starting gold price producer...")
        # Get the absolute path to the project root
        project_root = Path(__file__).parent.parent.absolute()
        
        # Run the producer script
        result = subprocess.run(
            [sys.executable, "-m", "gold_streaming_demo.kafka_utils.producer"],
            cwd=str(project_root),
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(result.stdout)
        logger.info("Gold price producer completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Producer failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in producer: {str(e)}")
        return False

def run_consumer_process():
    """Run the gold price consumer in a separate process."""
    try:
        logger.info("Starting gold price consumer...")
        # Get the absolute path to the project root
        project_root = Path(__file__).parent.parent.absolute()
        
        # Run the consumer script
        result = subprocess.run(
            [sys.executable, "-m", "gold_streaming_demo.kafka_utils.consumer"],
            cwd=str(project_root),
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(result.stdout)
        logger.info("Gold price consumer completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Consumer failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in consumer: {str(e)}")
        return False

def main():
    """Main function to run the entire pipeline with producer and consumer running simultaneously."""
    logger.info("Starting gold streaming pipeline...")
    
    # Step 1: Start Kafka server
    if not start_kafka_server():
        logger.error("Failed to start Kafka server. Exiting.")
        return
    
    # Give Kafka some time to fully start
    logger.info("Waiting for Kafka to initialize...")
    time.sleep(10)
    
    # Step 2: Run the producer and consumer simultaneously
    logger.info("Starting producer and consumer simultaneously...")
    
    # Create processes for producer and consumer
    producer_process = multiprocessing.Process(target=run_producer_process)
    consumer_process = multiprocessing.Process(target=run_consumer_process)
    
    # Start both processes
    producer_process.start()
    consumer_process.start()
    
    # Wait for both processes to complete
    producer_process.join()
    consumer_process.join()
    
    # Check if both processes completed successfully
    if producer_process.exitcode != 0:
        logger.error("Producer process failed.")
        return
    
    if consumer_process.exitcode != 0:
        logger.error("Consumer process failed.")
        return
    
    logger.info("Gold streaming pipeline completed successfully.")

if __name__ == "__main__":
    main() 