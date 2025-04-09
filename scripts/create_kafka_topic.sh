#!/bin/bash

echo "create topic script"
# Set error handling
set -e

# Default configuration
KAFKA_VERSION="kafka_2.13-3.9.0"
KAFKA_HOME="$HOME/$KAFKA_VERSION"

# Use environment variables with defaults
BOOTSTRAP_SERVER=${KAFKA_BOOTSTRAP_SERVERS:-"localhost:9092"}
TOPIC_NAME=${KAFKA_TOPIC_NAME:-"gold_price_stream"}
PARTITIONS=1
REPLICATION_FACTOR=1

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Using Kafka installation at: $KAFKA_HOME"
echo "Using bootstrap server: $BOOTSTRAP_SERVER"

# Create the topic
echo "Creating Kafka topic: $TOPIC_NAME"
cd "$KAFKA_HOME"
bin/kafka-topics.sh --create \
    --bootstrap-server "$BOOTSTRAP_SERVER" \
    --replication-factor "$REPLICATION_FACTOR" \
    --partitions "$PARTITIONS" \
    --topic "$TOPIC_NAME"
cd - > /dev/null

# Verify the topic was created
echo "Verifying topic creation..."
cd "$KAFKA_HOME"
bin/kafka-topics.sh --list --bootstrap-server "$BOOTSTRAP_SERVER" | grep "$TOPIC_NAME"
cd - > /dev/null

echo "Kafka topic '$TOPIC_NAME' created successfully!" 