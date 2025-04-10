# Gold Price Streaming Pipeline

A real-time data pipeline for streaming gold price data using Kafka and Dagster.

## Overview

This project implements a data pipeline that:
1. Fetches gold price data from Yahoo Finance
2. Streams the data through Apache Kafka
3. Consumes and stores the data in S3
4. Orchestrates the entire process using Dagster

## Prerequisites

- Python 3.8+
- Apache Kafka
- AWS S3 bucket
- Docker (for running Kafka)

## Installation

0. sudo yum install git
1. Clone the repository:
```bash
git clone <repository-url>
cd gold-streaming-demo
```

2. Install dependencies using Poetry:
pip3 install poetry
```bash
poetry install
```

3. Set up environment variables:
```bash
export KAFKA_BOOTSTRAP_SERVERS=3.106.251.171:9092
```
and other optional


## Usage

### Setting Up Kafka Topics

Before running the pipeline, you need to create the Kafka topic that will be used for streaming gold price data:
0.
chmod +x scripts/kafka_start.sh 
chmod +x scripts/create_kafka_topic.sh 

1. Start Kafka and Zookeeper:
```bash
sh ./scripts/kafka_start.sh
```
2. Setup topic
```bash
sh ./scripts/create_kafka_topic.sh
```

### Running the Pipeline

1. Start the Dagster UI:
```bash
poetry run dagster dev -f gold_streaming_demo/assets.py -h 0.0.0.0 -p 3000
```

2. The pipeline will:
   - Run the producer to fetch and stream gold price data
   - Run the consumer to process and store data in S3
