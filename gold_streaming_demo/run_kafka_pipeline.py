import logging
import multiprocessing
import subprocess
import time
from pathlib import Path

from gold_streaming_demo.kafka_utils.consumer import run_consumer
from gold_streaming_demo.kafka_utils.producer import run_producer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def start_kafka_server() -> bool:
    """Start Kafka and Zookeeper servers.

    Returns:
        bool: True if Kafka and Zookeeper started successfully, False otherwise.
    """
    try:
        logger.info("Starting Kafka & Zookeeper...")

        # Check if scripts directory exists
        scripts_dir = Path("./scripts")
        if not scripts_dir.exists():
            logger.error(f"Scripts directory not found at {scripts_dir.absolute()}")
            return False

        script_path = scripts_dir / "kafka_start.sh"
        stop_path = scripts_dir / "kafka_stop.sh"

        # Check if scripts exist
        if not script_path.exists():
            logger.error(f"Kafka start script not found at {script_path.absolute()}")
            return False

        if not stop_path.exists():
            logger.warning(f"Kafka stop script not found at {stop_path.absolute()}")

        # Make scripts executable
        try:
            script_path.chmod(0o755)
            if stop_path.exists():
                stop_path.chmod(0o755)
        except Exception as e:
            logger.error(f"Failed to make scripts executable: {str(e)}")
            return False

        # Run the start script with detailed output
        logger.info(f"Executing Kafka start script: {script_path.absolute()}")
        result = subprocess.run(
            [str(script_path)], check=True, capture_output=True, text=True
        )

        # Log the output
        if result.stdout:
            logger.info(f"Kafka start script output: {result.stdout}")
        if result.stderr:
            logger.warning(f"Kafka start script warnings: {result.stderr}")

        logger.info("Kafka & Zookeeper started successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Kafka: {e.stderr}")
        logger.error(f"Exit code: {e.returncode}")
        logger.error(f"Command: {e.cmd}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error starting Kafka: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def run_producer_process() -> bool:
    """Run the gold price producer in a separate process.

    Returns:
        bool: True if producer completed successfully, False otherwise.
    """
    try:
        logger.info("Starting gold price producer...")
        run_producer()
        logger.info("Gold price producer completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Producer failed: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def run_consumer_process() -> bool:
    """Run the gold price consumer in a separate process.

    Returns:
        bool: True if consumer started successfully, False otherwise.
        Note: This function may run indefinitely as it continuously consumes messages.
    """
    try:
        logger.info("Starting gold price consumer...")
        run_consumer()
        # Note: This function may run indefinitely
        return True
    except Exception as e:
        logger.error(f"Consumer failed: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def main() -> None:
    """Main function to run the entire pipeline with producer and consumer running simultaneously.

    This function:
    1. Starts the Kafka server
    2. Waits for Kafka to initialize
    3. Runs the producer and consumer in separate processes
    4. Monitors the processes and handles graceful shutdown

    Returns:
        None
    """
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

    # Wait for the producer to complete (it should finish after sending all data)
    producer_process.join()

    # Check if producer completed successfully
    if producer_process.exitcode != 0:
        logger.error("Producer process failed.")
        # Terminate the consumer process if producer failed
        consumer_process.terminate()
        return

    logger.info(
        "Producer completed successfully. Consumer is still running in the background."
    )
    logger.info(
        "The consumer will continue to process messages until manually stopped."
    )
    logger.info("To stop the consumer, press Ctrl+C or close this terminal.")

    try:
        # Keep the main process running to allow the consumer to continue
        while consumer_process.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Stopping consumer...")
        consumer_process.terminate()
        consumer_process.join(timeout=5)
        if consumer_process.is_alive():
            logger.warning(
                "Consumer did not terminate gracefully. Forcing termination."
            )
            consumer_process.kill()

    logger.info("Gold streaming pipeline completed.")


if __name__ == "__main__":
    main()
