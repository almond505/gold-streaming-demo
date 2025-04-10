# Gold Price Streaming Pipeline

A real-time data pipeline for streaming gold price data using Kafka and AWS.

![Pipeline Architecture](https://file.notion.so/f/f/dfde445b-a682-4c4a-8e17-3aa9ecc07c6c/01335b76-b0af-460b-9a3d-651ed199e7e3/image.png?table=block&id=1d10c130-b082-80e7-8464-f2c5366dff82&spaceId=dfde445b-a682-4c4a-8e17-3aa9ecc07c6c&expirationTimestamp=1744322400000&signature=7I963w80L57sYPW3qOEt8TsTsp610EorjZROqzAqlSE&downloadName=image.png)

## Overview

This project implements a data pipeline that:
1. Fetches gold price data from Yahoo Finance
2. Streams the data through Apache Kafka
3. Consumes and stores the data in S3 Bucket
4. (Optional) AWS Glue Crawler from S3 Bucket to Data Catalog
5. (Optional) Query in Athena

## Prerequisites

- Python 3.8+
- Apache Kafka
- AWS S3 bucket
- Poetry (Python package manager)
- An AWS EC2 instance running Amazon Linux 2, Ubuntu, or another Linux distribution
- SSH access to your EC2 instance
- Sufficient permissions to install software and configure security groups

## Setting Up AWS EC2

### Step 1: Install Java
```bash
sudo yum update -y
sudo yum install java-1.8.0-openjdk
```

### Step 2: Download and Install Kafka
```bash
wget https://downloads.apache.org/kafka/3.3.1/kafka_2.12-3.3.1.tgz
tar -xvf kafka_2.12-3.3.1.tgz
```

### Step 3: Install Git if not already installed:
```bash
sudo yum install git
```

### Step 4: Configure EC2 Security Group
You need to open the following ports in your EC2 security group:
- Port 2181: Zookeeper
- Port 9092: Kafka

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gold-streaming-demo
```

2. Install dependencies using Poetry:
```bash
pip3 install poetry
poetry install
```

3. Set up environment variables:
```bash
# Kafka configuration
export KAFKA_BOOTSTRAP_SERVERS=your_kafka_server:9092

# Dagster configuration
export DAGSTER_HOME=~/dagster

# AWS configuration
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Add other optional environment variables as needed
```

## Usage

### Setting Up Kafka Topics

Before running the pipeline for the first time, you need to create the Kafka topic that will be used for streaming gold price data:

1. Make the scripts executable:
```bash
chmod +x scripts/kafka_start.sh
chmod +x scripts/create_kafka_topic.sh
```

2. Start Kafka and Zookeeper:
```bash
sh ./scripts/kafka_start.sh
```

3. Create the Kafka topic:
```bash
sh ./scripts/create_kafka_topic.sh
```

4. Stop Kafka and Zookeeper:
```bash
sh ./scripts/kafka_stop.sh
```

### Running the Pipeline

1. Start the Dagster UI:
```bash
poetry run dagster dev -f gold_streaming_demo/assets.py -h 0.0.0.0 -p 3000
```

2. The pipeline will:
   - Start Kafka and Zookeeper
   - Run the producer to fetch and stream gold price data
   - Run the consumer to process and store data in S3

## Future Development

The following features are planned for future development:

### 1. Orchestration
- Implement Dagster for workflow orchestration (TODO)
- Alternative orchestration tools to consider:
  - Apache Airflow
  - Prefect
  - Luigi

### 2. Environment Configuration
- Create a `.env` file template for environment variables
- Implement environment variable validation

### 3. Logging and Monitoring
- Implement structured logging using Python's logging module
- Create a logging database for:
  - Pipeline execution metrics
  - Error tracking
  - Performance monitoring
  - Audit trails
