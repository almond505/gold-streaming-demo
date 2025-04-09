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

1. Clone the repository:
```bash
git clone <repository-url>
cd gold-streaming-demo
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up environment variables:
```bash
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
export KAFKA_TOPIC_NAME=gold_price_stream
export KAFKA_CONSUMER_GROUP=gold_price_group
export S3_BUCKET_NAME=your-bucket-name
export S3_PREFIX=gold_price
```

## Project Structure

```
gold_streaming_demo/
├── gold_streaming_demo/
│   ├── __init__.py
│   ├── assets.py          # Dagster assets
│   ├── config.py          # Configuration management
│   └── kafka_utils/
│       ├── producer.py    # Kafka producer
│       └── consumer.py    # Kafka consumer
├── scripts/
│   └── kafka_start.sh     # Kafka startup script
├── pyproject.toml         # Project dependencies
└── dagster.yaml          # Dagster configuration
```

## Usage

1. Start the Dagster UI:
```bash
dagster dev
```

2. The pipeline will:
   - Start Kafka and Zookeeper
   - Run the producer to fetch and stream gold price data
   - Run the consumer to process and store data in S3

## Configuration

The pipeline can be configured through environment variables or by modifying the `config.py` file:

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
- `KAFKA_TOPIC_NAME`: Kafka topic name
- `KAFKA_CONSUMER_GROUP`: Consumer group ID
- `S3_BUCKET_NAME`: S3 bucket name
- `S3_PREFIX`: Prefix for S3 objects

## Error Handling

The pipeline includes comprehensive error handling and logging:
- All components log to stdout with proper formatting
- Errors are caught and logged with appropriate context
- Failed operations are retried where appropriate

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
