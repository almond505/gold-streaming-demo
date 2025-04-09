#!/bin/bash

# Set error handling
set -e

# Default values
BOOTSTRAP_SERVER="localhost:9092"
TOPIC_NAME="gold_price_stream"
PARTITIONS=1
REPLICATION_FACTOR=1

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find Kafka installation
find_kafka() {
    # Check common installation paths
    local kafka_paths=(
        "./kafka_2.12-3.3.1"
        "../kafka_2.12-3.3.1"
        "/usr/local/kafka"
        "/opt/kafka"
        "$HOME/kafka"
    )
    
    for path in "${kafka_paths[@]}"; do
        if [ -d "$path" ] && [ -f "$path/bin/kafka-topics.sh" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # If not found, check if kafka is in PATH
    if command_exists kafka-topics.sh; then
        echo "kafka in PATH"
        return 0
    fi
    
    return 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --bootstrap-server)
            BOOTSTRAP_SERVER="$2"
            shift 2
            ;;
        --topic)
            TOPIC_NAME="$2"
            shift 2
            ;;
        --partitions)
            PARTITIONS="$2"
            shift 2
            ;;
        --replication-factor)
            REPLICATION_FACTOR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Find Kafka installation
KAFKA_HOME=$(find_kafka)

if [ -z "$KAFKA_HOME" ]; then
    echo "Error: Kafka installation not found. Please install Kafka or set KAFKA_HOME environment variable."
    exit 1
fi

echo "Using Kafka installation at: $KAFKA_HOME"

# Create the topic
echo "Creating Kafka topic: $TOPIC_NAME"
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    kafka-topics.sh --create \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --replication-factor "$REPLICATION_FACTOR" \
        --partitions "$PARTITIONS" \
        --topic "$TOPIC_NAME"
else
    "$KAFKA_HOME/bin/kafka-topics.sh" --create \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --replication-factor "$REPLICATION_FACTOR" \
        --partitions "$PARTITIONS" \
        --topic "$TOPIC_NAME"
fi

# Verify the topic was created
echo "Verifying topic creation..."
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    kafka-topics.sh --list --bootstrap-server "$BOOTSTRAP_SERVER" | grep "$TOPIC_NAME"
else
    "$KAFKA_HOME/bin/kafka-topics.sh" --list --bootstrap-server "$BOOTSTRAP_SERVER" | grep "$TOPIC_NAME"
fi

echo "Kafka topic '$TOPIC_NAME' created successfully!" 