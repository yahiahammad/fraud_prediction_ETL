from confluent_kafka import Consumer, KafkaError
import json
import pandas as pd
import time
import pymysql
import xgboost as xgb

FEATURES = [
    'Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 
    'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 
    'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 
    'V28', 'Amount'
]

def initialize_database(conn):
    try:
        with conn.cursor() as cursor:
            # offset as the primary key
            create_table_query = """
            CREATE TABLE IF NOT EXISTS scored_payments (
                id BIGINT PRIMARY KEY,
                amount DECIMAL(15, 2),
                fraud_score FLOAT,
                is_fraud TINYINT(1),
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_query)
        conn.commit()
        print("table scored_payments is ready")
    except Exception as e:
        print(f"table error: {e}")
        exit(1)

def insert_scored_payment(conn, msg, payment_id, amount, fraud_score, is_fraud, consumer):
    try:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO scored_payments (id, amount, fraud_score, is_fraud)
            VALUES (%s, %s, %s, %s);
            """
            cursor.execute(insert_query, (payment_id, amount, fraud_score, is_fraud))
        conn.commit()
        print(f"inserted payment id {payment_id} with fraud score {fraud_score}")
        consumer.commit(message = msg, asynchronous=False)
        print(f"committed offset for payment id {payment_id}")
    except Exception as e:
        print(f"insert error: {e}")

def pull_transactions(consumer):
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"transacion pulling error: {msg.error()}")
            continue

        record = json.loads(msg.value().decode('utf-8'))
        df = pd.DataFrame([record])
        df = df[FEATURES]
        yield msg, df

c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'payment-group',
    'auto.offset.reset': 'latest' #change to earliest/latest to read from the beginning/end (model was paused and you need to resume again/fresh start)
})

c.subscribe(['payment-topic'])

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    database='scoring_db'
)

model = xgb.Booster()
model.load_model('fraud_model.json')


initialize_database(connection)

#main loop

for msg, transaction_df in pull_transactions(c):
    dmatrix = xgb.DMatrix(transaction_df)
    fraud_score = model.predict(dmatrix)[0]
    is_fraud = int(fraud_score > 0.6)
    amount = transaction_df['Amount'].iloc[0]
    insert_scored_payment(connection, msg, msg.offset(), amount, float(fraud_score), is_fraud, c)
    time.sleep(1)