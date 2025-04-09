#!/bin/bash

# Start Zookeeper (background)
bin/zookeeper-server-start.sh config/zookeeper.properties

# Wait for Zookeeper to start
sleep 5

# Start Kafka server (background)
export KAFKA_HEAP_OPTS="-Xmx256M -Xms128M"
cd kafka_2.12-3.3.1
bin/kafka-server-start.sh config/server.properties