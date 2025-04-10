#!/bin/bash

echo "start script"
# Set error handling
set -e

# Default configuration
KAFKA_HEAP_OPTS="-Xmx256M -Xms128M"
ZOOKEEPER_PORT=2181
KAFKA_PORT=9092
KAFKA_LOG_DIR="/tmp/kafka-logs"
ZOOKEEPER_LOG_DIR="/tmp/zookeeper"
KAFKA_VERSION="kafka_2.13-3.9.0"

KAFKA_HOME="$HOME/$KAFKA_VERSION"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    local port=$1
    if command_exists lsof; then
        lsof -i :$port > /dev/null 2>&1
        return $?
    elif command_exists netstat; then
        netstat -an | grep ":$port " | grep LISTEN > /dev/null 2>&1
        return $?
    else
        echo "Warning: Cannot check if port $port is in use. Please install lsof or netstat."
        return 1
    fi
}


echo "Using Kafka installation at: $KAFKA_HOME"

# Create log directories if they don't exist
mkdir -p "$KAFKA_LOG_DIR" "$ZOOKEEPER_LOG_DIR"

# Check if ports are already in use
if port_in_use $ZOOKEEPER_PORT; then
    echo "Error: Port $ZOOKEEPER_PORT is already in use. Zookeeper may already be running."
    exit 1
fi

if port_in_use $KAFKA_PORT; then
    echo "Error: Port $KAFKA_PORT is already in use. Kafka may already be running."
    exit 1
fi

# Start Zookeeper
echo "Starting Zookeeper on port $ZOOKEEPER_PORT..."
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    zookeeper-server-start.sh -daemon config/zookeeper.properties
else
    cd "$KAFKA_HOME"
    bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
    cd - > /dev/null
fi

# Wait for Zookeeper to start
echo "Waiting for Zookeeper to start..."
sleep 5

# Start Kafka server
echo "Starting Kafka server on port $KAFKA_PORT..."
export KAFKA_HEAP_OPTS="$KAFKA_HEAP_OPTS"
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    kafka-server-start.sh -daemon config/server.properties
else
    cd "$KAFKA_HOME"
    bin/kafka-server-start.sh -daemon config/server.properties
    cd - > /dev/null
fi

echo "Kafka and Zookeeper started successfully!"
echo "Kafka is running on port $KAFKA_PORT"
echo "Zookeeper is running on port $ZOOKEEPER_PORT"
echo "To stop Kafka and Zookeeper, use: ./scripts/kafka_stop.sh"
