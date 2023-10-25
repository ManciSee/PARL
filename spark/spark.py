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

def elaborate(batch_df: DataFrame, batch_id: int):
    batch_df.show(truncate=False)

# Create a Spark context and session
sc = SparkContext(appName="StreamingKafka")
spark = SparkSession(sc)
sc.setLogLevel("ERROR")

kafkaServer = "kafka:39092"
topic = "speech"

# Define the schema for the JSON data
schema = StructType([
    StructField("id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("text", StringType(), True),
    StructField("duration", StringType(), True)
])

def write_to_csv(record):
    # Define the path to the CSV file where you want to save the data
    csv_file_path = "/app/transcription.csv"
    
    # Define the column names
    column_names = ["id", "timestamp", "text", "duration"]

    # If the file does not exist, write the column names as the header
    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
    
    # Append the data to the CSV file
    with open(csv_file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([record['id'], record['timestamp'], record['text'], record['duration']])

# Read from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topic) \
    .load()

# Deserialize the value from Kafka as JSON
df = df.selectExpr("CAST(value AS STRING)")

# Apply the schema to the JSON data
df = df.select(from_json("value", schema).alias("data"))

# Select the individual columns
df = df.select("data.id", "data.timestamp", "data.text", "data.duration")

# Write to CSV file
df.writeStream \
    .foreach(write_to_csv) \
    .start() \
    .awaitTermination()

print("Done!")
