#!/bin/bash

# Set error handling
set -e

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
        if [ -d "$path" ] && [ -f "$path/bin/kafka-server-start.sh" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # If not found, check if kafka is in PATH
    if command_exists kafka-server-start.sh; then
        echo "kafka in PATH"
        return 0
    fi
    
    return 1
}

# Find Kafka installation
KAFKA_HOME=$(find_kafka)

if [ -z "$KAFKA_HOME" ]; then
    echo "Error: Kafka installation not found. Please install Kafka or set KAFKA_HOME environment variable."
    exit 1
fi

echo "Using Kafka installation at: $KAFKA_HOME"

# Start Zookeeper
echo "Starting Zookeeper..."
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    zookeeper-server-start.sh config/zookeeper.properties &
else
    "$KAFKA_HOME/bin/zookeeper-server-start.sh" "$KAFKA_HOME/config/zookeeper.properties" &
fi

# Wait for Zookeeper to start
echo "Waiting for Zookeeper to start..."
sleep 5

# Start Kafka server
echo "Starting Kafka server..."
export KAFKA_HEAP_OPTS="-Xmx256M -Xms128M"
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    kafka-server-start.sh config/server.properties
else
    "$KAFKA_HOME/bin/kafka-server-start.sh" "$KAFKA_HOME/config/server.properties"
fi