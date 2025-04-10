from kafka import KafkaConsumer
import json
import logging
from datetime import datetime
from s3fs import S3FileSystem
from gold_streaming_demo.config import KafkaConfig, S3Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_consumer(config: KafkaConfig) -> KafkaConsumer:
    """Create and return a Kafka consumer with the given configuration."""
    try:
        logger.info(f"Creating Kafka consumer with bootstrap servers: {config.bootstrap_servers}")
        return KafkaConsumer(
            config.topic_name,
            bootstrap_servers=config.bootstrap_servers,
            # group_id=config.consumer_group,
            # auto_offset_reset='earliest',
            # enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    except Exception as e:
        logger.error(f"Failed to create Kafka consumer: {str(e)}")
        raise

def save_to_s3(s3: S3FileSystem, data: dict, config: S3Config, count: int):
    """Save data to S3 with proper error handling."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message_id = data.get('Datetime')
        if message_id:
            filename = f"{config.prefix}_{message_id}.json"
        else:
            filename = f"{config.prefix}_{timestamp}_{count}.json"
        s3_path = f"s3://{config.bucket_name}/{filename}"
        
        if not s3.exists(s3_path):
            with s3.open(s3_path, 'w') as file:
                json.dump(data, file)
        else:
            logger.info(f"{s3_path} already exists. Skipping.")

        logger.info(f"Successfully saved data to {s3_path}")
    except Exception as e:
        logger.error(f"Failed to save data to S3: {str(e)}")
        raise

def process_messages(consumer: KafkaConsumer, s3: S3FileSystem, config: S3Config):
    """Process messages from Kafka and save to S3."""
    try:
        for count, message in enumerate(consumer):
            try:
                data = message.value
                save_to_s3(s3, data, config, count)
            except Exception as e:
                logger.error(f"Failed to process message {count}: {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Error in message processing loop: {str(e)}")
        raise

def run_consumer():
    """Main function to run the consumer."""
    try:
        kafka_config = KafkaConfig()
        s3_config = S3Config()
        
        consumer = create_consumer(kafka_config)
        s3 = S3FileSystem()
        
        logger.info("Starting to consume messages...")
        process_messages(consumer, s3, s3_config)
        
    except Exception as e:
        logger.error(f"Consumer failed: {str(e)}")
        raise
    finally:
        if 'consumer' in locals():
            consumer.close()

# Add this to make the file executable as a standalone script
if __name__ == "__main__":
    run_consumer()
