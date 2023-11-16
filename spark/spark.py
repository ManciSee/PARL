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


#------------------------------------------------------------------------------------------------------------
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


    # Leggi il dataset CSV dopo il salvataggio
    dataset = pd.read_csv(csv_file_path)

    # Fissa il seed per il generatore di numeri casuali per rendere l'esecuzione più deterministica
    np.random.seed(42)

    # Inizializza il dizionario e la matrice dei documenti
    dictionary = corpora.Dictionary()

    # Lista per memorizzare i risultati
    results = []

    # Itera su ogni riga del dataset
    for index, row in dataset.iterrows():
        # Prepara il documento per la topic modeling
        document = preprocess_string(row['text'])

        # Aggiungi il documento al dizionario
        dictionary.add_documents([document])

        # Creazione della matrice del documento
        bow = dictionary.doc2bow(document)

        # Definizione del modello di topic modeling
        lda_model = LdaModel([bow], num_topics=3, id2word=dictionary, passes=15)

        # Esegui la topic modeling per il documento corrente
        topics = lda_model[bow]

        # Trova il topic più dominante
        dominant_topic = max(topics, key=lambda x: x[1])
        topic_index, topic_score = dominant_topic

        # Estrai i termini principali, rimuovendo numeri e '*'
        top_terms = [term for term, _ in lda_model.show_topic(topic_index, topn=3) if not (term.isdigit() or '*' in term)]

        # Aggiungi i risultati alla lista
        results.append({
            'ID': row['id'],
            'Topic': topic_index,
            'Score': topic_score,
            'Top Terms': ' , '.join(top_terms)
        })
    es_data = {
        "id": record['id'],
        "timestamp": record['timestamp'],
        "text": record['text'],
        "duration": record['duration'],
        "topic": topic_index,
        "score": topic_score,
        "top_terms": ', '.join(top_terms)
    }
    es.index(index=elastic_index, body=es_data, ignore=400)

    # Stampa i risultati
    for result in results:
        print(f"ID: {result['ID']}, Topic: {result['Topic']}, Score: {result['Score']}")
        print(f"Top Terms: {result['Top Terms']}")
        print()

    # Salvataggio dei risultati in un file CSV
    output_df = pd.DataFrame(results, columns=['ID', 'Topic', 'Score', 'Top Terms'])
    output_df.to_csv('output.csv', index=False)

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