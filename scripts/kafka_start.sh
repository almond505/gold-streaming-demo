#!/bin/bash

# Set error handling
set -e

# Default configuration
KAFKA_HEAP_OPTS="-Xmx256M -Xms128M"
ZOOKEEPER_PORT=2181
KAFKA_PORT=9092
KAFKA_LOG_DIR="/tmp/kafka-logs"
ZOOKEEPER_LOG_DIR="/tmp/zookeeper"
KAFKA_VERSION="kafka_2.12-3.3.1"

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

# Function to find Kafka installation
find_kafka() {
    # Check common installation paths
    local kafka_paths=(
        "./$KAFKA_VERSION"
        "../$KAFKA_VERSION"
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

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --kafka-heap-opts)
            KAFKA_HEAP_OPTS="$2"
            shift 2
            ;;
        --zookeeper-port)
            ZOOKEEPER_PORT="$2"
            shift 2
            ;;
        --kafka-port)
            KAFKA_PORT="$2"
            shift 2
            ;;
        --kafka-log-dir)
            KAFKA_LOG_DIR="$2"
            shift 2
            ;;
        --zookeeper-log-dir)
            ZOOKEEPER_LOG_DIR="$2"
            shift 2
            ;;
        --kafka-version)
            KAFKA_VERSION="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --kafka-heap-opts <opts>     Set Kafka heap options (default: -Xmx256M -Xms128M)"
            echo "  --zookeeper-port <port>      Set Zookeeper port (default: 2181)"
            echo "  --kafka-port <port>          Set Kafka port (default: 9092)"
            echo "  --kafka-log-dir <dir>        Set Kafka log directory (default: /tmp/kafka-logs)"
            echo "  --zookeeper-log-dir <dir>    Set Zookeeper log directory (default: /tmp/zookeeper)"
            echo "  --kafka-version <version>    Set Kafka version (default: kafka_2.12-3.3.1)"
            echo "  --help                        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
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