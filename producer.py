from confluent_kafka import Producer
import pandas as pd
import json
import time


p = Producer({'bootstrap.servers': 'localhost:9092'})

data = pd.read_csv('dataset/creditcard.csv').drop('Class', axis=1)

for _, row in data.iterrows():
    currentrow = row.to_dict()
    p.produce('payment-topic', json.dumps(currentrow).encode('utf-8'))
    p.flush()
    time.sleep(1)