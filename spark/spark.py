# from __future__ import print_function
# import sys
# import os
# from pyspark import SparkContext, SparkConf
# from pyspark.sql import SparkSession
# from pyspark.streaming import StreamingContext
# from pyspark.sql.dataframe import DataFrame
# from elasticsearch import Elasticsearch
# import csv
# import json
# from pyspark.sql.functions import from_json
# from pyspark.sql.types import StructType, StructField, StringType
# import pandas as pd

# def elaborate(batch_df: DataFrame, batch_id: int):
#     batch_df.show(truncate=False)

# # Create a Spark context and session
# SparkConf = SparkConf().set("es.nodes", "elasticsearch").set("es.port", "9200")
# sc = SparkContext(conf=SparkConf, appName="StreamingKafka")
# spark = SparkSession(sc)
# sc.setLogLevel("ERROR")

# # Kafka
# kafkaServer = "kafka:39092"
# topic = "speech"

# # Elasticsearch
# elastic_host = "http://elasticsearch:9200"
# elastic_index = "speech"

# es_mapping = {
#     "mappings": {
#         "properties": {
#             "timestamp": {
#                 "type": "date",
#                 "format": "yyyy-MM-dd'T'HH:mm:ss"
#             },
#             "text": {
#                 "type": "text",
#                 "fielddata": True
#             },
#             "duration": {
#                 "type": "float"
#             }
#         }
#     }
# }



# schema = StructType([
#     StructField("id", StringType(), True),
#     StructField("timestamp", StringType(), True),
#     StructField("text", StringType(), True),
#     StructField("duration", StringType(), True)
# ])

# # def write_to_csv(record):
# #     csv_file_path = "/app/transcription.csv"
# #     column_names = ["id", "timestamp", "text", "duration"]

# #     if not os.path.isfile(csv_file_path):
# #         with open(csv_file_path, 'w', newline='') as f:
# #             writer = csv.writer(f)
# #             writer.writerow(column_names)
    
# #     with open(csv_file_path, 'a', newline='') as f:
# #         writer = csv.writer(f)
# #         writer.writerow([record['id'], record['timestamp'], record['text'], record['duration']])

# def write_to_csv_and_send_to_es(record):
#     csv_file_path = "/app/transcription.csv"
#     column_names = ["id", "timestamp", "text", "duration"]

#     if not os.path.isfile(csv_file_path):
#         with open(csv_file_path, 'w', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow(column_names)
    
#     with open(csv_file_path, 'a', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([record['id'], record['timestamp'], record['text'], record['duration']])
    
#     # Create Elasticsearch client inside the function
#     es = Elasticsearch(elastic_host)
    
#     # Send data to Elasticsearch
#     es_data = {
#         "id": record['id'],
#         "timestamp": record['timestamp'],
#         "text": record['text'],
#         "duration": record['duration']
#     }
#     es.index(index=elastic_index, body=es_data, ignore=400)

# print("Reading from Kafka...")
# df = spark \
#     .readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", kafkaServer) \
#     .option("subscribe", topic) \
#     .load()

# df = df.selectExpr("CAST(value AS STRING)")
# df = df.select(from_json("value", schema).alias("data"))
# df = df.select("data.id", "data.timestamp", "data.text", "data.duration")

# print("Save to CSV and send to Elasticsearch...")
# df.writeStream \
#     .foreach(write_to_csv_and_send_to_es) \
#     .start() \
#     .awaitTermination()
# print("Done!")


#--------------------------------------------------------------------------------------------------------------------
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
from gensim import corpora
from gensim.models import LdaModel
from gensim.parsing.preprocessing import preprocess_string
import re
import numpy as np
from typing import Set


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

def write_to_csv_and_send_to_es(record):
    csv_file_path = "/app/transcription.csv"
    column_names = ["id", "timestamp", "text", "duration"]

    is_empty = os.stat(csv_file_path).st_size == 0

    if is_empty:
        # If the CSV file is empty, add a new row with initial data
        initial_data = ["2023-11-22T17:01:59", "2023-11-22T17:01:59", "Initial control phrase", 10.56848359107971]
        with open(csv_file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
            writer.writerow(initial_data)
    
    # Create Elasticsearch client inside the function
    es = Elasticsearch(elastic_host)

    processed_ids = set()
    if record['id'] in processed_ids:
        print(f"Record with ID {record['id']} already processed. Skipping.")
        return

    # Uncomment the following lines to open the CSV file in append mode
    with open(csv_file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([record['id'], record['timestamp'], record['text'], record['duration']])

    processed_ids.add(record['id'])

    # topic modelling
    dataset = pd.read_csv(csv_file_path)

    np.random.seed(42)

    dictionary = corpora.Dictionary()

    results = []

    print("Finding topic...")
    # Itera su ogni riga del dataset
    for index, row in dataset.iterrows():
        document = preprocess_string(row['text'])
        dictionary.add_documents([document])

        bow = dictionary.doc2bow(document)
        lda_model = LdaModel([bow], num_topics=3, id2word=dictionary, passes=15)

        topics = lda_model[bow]
        dominant_topic = max(topics, key=lambda x: x[1])
        topic_index, topic_score = dominant_topic

        # 3 Topic
        top_terms = [term for term, _ in lda_model.show_topic(topic_index, topn=3) if not (term.isdigit() or '*' in term)]

        # 1 Topic
        unique_topic = top_terms[0] if top_terms else None

        results.append({
            'ID': row['id'],
            'Topic': topic_index,
            'Score': topic_score,
            'Top Terms': ' , '.join(top_terms),
            'Unique Topic': unique_topic

        })
    print("Done!")

    es_data = {
        "id": record['id'],
        "timestamp": record['timestamp'],
        "text": record['text'],
        "duration": record['duration'],
        "topic": topic_index,
        "score": topic_score,
        "top_terms": ', '.join(top_terms),
        "unique_topic": unique_topic

    }
    es.index(index=elastic_index, body=es_data, ignore=400)

    print("Send data and topics to es!")

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

print("Saving to CSV and sending to Elasticsearch...")
df.writeStream \
    .foreach(write_to_csv_and_send_to_es) \
    .start() \
    .awaitTermination()