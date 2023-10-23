from __future__ import print_function

import sys

from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.dataframe import DataFrame
from elasticsearch import Elasticsearch


def elaborate(batch_df : DataFrame, batch_id: int):
    batch_df.show(truncate=False)

# SparkConf = SparkConf().set("es.nodes", "elasticsearch").set("es.port", "9200")
sc = SparkContext(appName="StreamingKafka")
spark = SparkSession(sc)   
sc.setLogLevel("WARN")

kafkaServer = "kafka:39092"
topic = "speech"

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topic) \
    .load()

df.selectExpr("CAST(timestamp AS STRING)", "CAST(value AS STRING)") \
    .writeStream \
    .format("console") \
    .start() \
    .awaitTermination()

    