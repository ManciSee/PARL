from __future__ import print_function
import sys
import os
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.dataframe import DataFrame
from elasticsearch import Elasticsearch
import csv
import json
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType
import pandas as pd

def elaborate(batch_df: DataFrame, batch_id: int):
    batch_df.show(truncate=False)

# Create a Spark context and session
SparkConf = SparkConf().set("es.nodes", "elasticsearch").set("es.port", "9200")
sc = SparkContext(conf=SparkConf, appName="StreamingKafka")
spark = SparkSession(sc)
sc.setLogLevel("ERROR")

# Kafka
kafkaServer = "kafka:39092"
topic = "speech"

# Elasticsearch
elastic_host = "http://elasticsearch:9200"
elastic_index = "speech"

es_mapping = {
    "mappings": {
        "properties": {
            "timestamp": {
                "type": "date",
                "format": "yyyy-MM-dd'T'HH:mm:ss"
            },
            "text": {
                "type": "text",
                "fielddata": True
            },
            "duration": {
                "type": "float"
            }
        }
    }
}



schema = StructType([
    StructField("id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("text", StringType(), True),
    StructField("duration", StringType(), True)
])

# def write_to_csv(record):
#     csv_file_path = "/app/transcription.csv"
#     column_names = ["id", "timestamp", "text", "duration"]

#     if not os.path.isfile(csv_file_path):
#         with open(csv_file_path, 'w', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow(column_names)
    
#     with open(csv_file_path, 'a', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([record['id'], record['timestamp'], record['text'], record['duration']])

def write_to_csv_and_send_to_es(record):
    csv_file_path = "/app/transcription.csv"
    column_names = ["id", "timestamp", "text", "duration"]

    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
    
    with open(csv_file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([record['id'], record['timestamp'], record['text'], record['duration']])
    
    # Create Elasticsearch client inside the function
    es = Elasticsearch(elastic_host)
    
    # Send data to Elasticsearch
    es_data = {
        "id": record['id'],
        "timestamp": record['timestamp'],
        "text": record['text'],
        "duration": record['duration']
    }
    es.index(index=elastic_index, body=es_data, ignore=400)

print("Reading from Kafka...")
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topic) \
    .load()

df = df.selectExpr("CAST(value AS STRING)")
df = df.select(from_json("value", schema).alias("data"))
df = df.select("data.id", "data.timestamp", "data.text", "data.duration")

print("Save to CSV and send to Elasticsearch...")
df.writeStream \
    .foreach(write_to_csv_and_send_to_es) \
    .start() \
    .awaitTermination()
print("Done!")

