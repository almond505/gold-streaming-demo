#!/usr/bin/env python
import subprocess
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_kafka():
    """Start Kafka and Zookeeper servers."""
    try:
        logger.info("Starting Kafka & Zookeeper...")
        
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        script_path = project_root / "scripts" / "kafka_start.sh"
        
        if not script_path.exists():
            raise FileNotFoundError(f"Kafka start script not found at {script_path}")
        
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Run the script
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

def main():
    """Main entry point for the script."""
    success = start_kafka()
    if not success:
        logger.error("Failed to start Kafka. Exiting with error code 1.")
        exit(1)
    logger.info("Kafka started successfully.")

if __name__ == "__main__":
    main() 