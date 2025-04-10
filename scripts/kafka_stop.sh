#!/bin/bash

echo "stop script"
# Set error handling
set -e

# Default configuration
ZOOKEEPER_PORT=2181
KAFKA_PORT=9092
KAFKA_VERSION="kafka_2.13-3.9.0"

KAFKA_HOME="$HOME/$KAFKA_VERSION"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Using Kafka installation at: $KAFKA_HOME"

# Stop Kafka server
echo "Stopping Kafka server..."
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    kafka-server-stop.sh || true
else
    cd "$KAFKA_HOME"
    bin/kafka-server-stop.sh || true
    cd - > /dev/null
fi

# Stop Zookeeper
echo "Stopping Zookeeper..."
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    zookeeper-server-stop.sh || true
else
    cd "$KAFKA_HOME"
    bin/zookeeper-server-stop.sh || true
    cd - > /dev/null
fi

# Verify processes are stopped
echo "Verifying processes are stopped..."
sleep 5

# Check if Kafka is still running
if command_exists lsof; then
    if lsof -i :$KAFKA_PORT > /dev/null 2>&1; then
        echo "Warning: Kafka may still be running on port $KAFKA_PORT"
        echo "You may need to manually kill the process"
    else
        echo "Kafka stopped successfully"
    fi
fi

# Check if Zookeeper is still running
if command_exists lsof; then
    if lsof -i :$ZOOKEEPER_PORT > /dev/null 2>&1; then
        echo "Warning: Zookeeper may still be running on port $ZOOKEEPER_PORT"
        echo "You may need to manually kill the process"
    else
        echo "Zookeeper stopped successfully"
    fi
fi
