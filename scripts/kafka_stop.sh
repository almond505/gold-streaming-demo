#!/bin/bash

# Set error handling
set -e

# Default configuration
ZOOKEEPER_PORT=2181
KAFKA_PORT=9092
KAFKA_VERSION="kafka_2.12-3.3.1"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
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
        if [ -d "$path" ] && [ -f "$path/bin/kafka-server-stop.sh" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # If not found, check if kafka is in PATH
    if command_exists kafka-server-stop.sh; then
        echo "kafka in PATH"
        return 0
    fi
    
    return 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --zookeeper-port)
            ZOOKEEPER_PORT="$2"
            shift 2
            ;;
        --kafka-port)
            KAFKA_PORT="$2"
            shift 2
            ;;
        --kafka-version)
            KAFKA_VERSION="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --zookeeper-port <port>      Set Zookeeper port (default: 2181)"
            echo "  --kafka-port <port>          Set Kafka port (default: 9092)"
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

# Stop Kafka server
echo "Stopping Kafka server..."
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    kafka-server-stop.sh
else
    cd "$KAFKA_HOME"
    bin/kafka-server-stop.sh
    cd - > /dev/null
fi

# Stop Zookeeper
echo "Stopping Zookeeper..."
if [ "$KAFKA_HOME" = "kafka in PATH" ]; then
    zookeeper-server-stop.sh
else
    cd "$KAFKA_HOME"
    bin/zookeeper-server-stop.sh
    cd - > /dev/null
fi

# Verify processes are stopped
echo "Verifying processes are stopped..."

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

echo "Kafka and Zookeeper stopped successfully!" 