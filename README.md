# Real-Time Fraud Detection Pipeline

This project implements a real-time fraud detection pipeline using Apache Kafka, XGBoost, and MySQL. It simulates transaction streaming, scores transactions on-the-fly using a trained machine learning model, and stores the results in a database.

## 🏗 Architecture

1.  **Producer (`producer.py`)**: Reads credit card transactions from a CSV dataset and publishes them to a Kafka topic (`payment-topic`).
2.  **Kafka**: Acts as the message broker for streaming transaction data.
3.  **Consumer (`consumer.py`)**: Subscribes to the Kafka topic, loads a pre-trained XGBoost model (`fraud_model.json`), predicts the probability of fraud for each transaction, and saves the results to MySQL.
4.  **MySQL**: Stores the scored transactions.
5.  **Kafdrop / Adminer**: Web UIs for monitoring Kafka and managing the database.

## 📋 Prerequisites

-   **Docker & Docker Compose**: For running the infrastructure (Kafka, MySQL, Zookeeper).
-   **Python 3.8+**
-   **Dataset**: The file `dataset/creditcard.csv` (Credit Card Fraud Detection dataset from [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud?resource=download)).

## ⚙️ Setup

### 1. Infrastructure Setup

Start the required services (Kafka, Zookeeper, MySQL, Kafdrop, Adminer) using Docker Compose:

```bash
docker-compose up -d
```

This will expose the following services:
-   **Kafka**: `localhost:9092`
-   **MySQL**: `localhost:3306` (User: `root`, Password: `password`, DB: `scoring_db`)
-   **Kafdrop** (Kafka UI): [http://localhost:9000](http://localhost:9000)
-   **Adminer** (Db UI): [http://localhost:8080](http://localhost:8080)

### 2. Python Environment

Install the required Python packages:

```bash
pip install confluent-kafka pandas pymysql xgboost
```

### 3. Model Training (Optional)
If `fraud_model.json` is missing or needs updating, run the Jupyter notebook:

1.  Open `model_training.ipynb`.
2.  Run all cells to train the XGBoost model and save it as `fraud_model.json`.

## 🚀 Usage

### Step 1: Start the Consumer
The consumer needs to be running to process incoming messages. It will automatically create the `scored_payments` table in the database if it doesn't exist.

```bash
python consumer.py
```

*Wait for it to initialize and subscribe to the topic.*

### Step 2: Start the Producer
The producer reads the dataset and streams transactions to Kafka (1 transaction every second).

```bash
python producer.py
```

## 📊 Monitoring & Validation

### Check Kafka Messages
Open **Kafdrop** at [http://localhost:9000](http://localhost:9000) and look for `payment-topic`. You should see the offset increasing.

### Check Database Results
Open **Adminer** at [http://localhost:8080](http://localhost:8080).
1.  **System**: MySQL
2.  **Server**: `mysql`
3.  **Username**: `root`
4.  **Password**: `password`
5.  **Database**: `scoring_db`

Query the `scored_payments` table to see the results:

```sql
SELECT * FROM scored_payments ORDER BY processed_at DESC;
```
