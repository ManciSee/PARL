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
import re
import numpy as np
from typing import Set
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googletrans import Translator
from langdetect import detect

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from operator import itemgetter

# Nltk
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

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
            },
            "summary": {
                "type": "text"
            }
        }
    }
}

schema = StructType([
    StructField("id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("text", StringType(), True),
    StructField("duration", StringType(), True),
    StructField("summary", StringType(), True)
])

def preprocess_text(text):
    from nltk.stem.porter import PorterStemmer
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords

    # Tokenization
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.isalnum()]

    detected_language = detect(text)

    # Stopwords
    stop_words = set()
    if detected_language == 'en':
        stop_words = set(stopwords.words('english'))
    elif detected_language == 'it':
        stop_words = set(stopwords.words('italian'))
    # Add more language cases as needed
    tokens = [word for word in tokens if word.lower() not in stop_words]

    # Bigram
    bigram_model = gensim.models.Phrases([tokens], min_count=1, threshold=1)
    bigram_phraser = gensim.models.phrases.Phraser(bigram_model)

    # Trigram
    trigram_model = gensim.models.Phrases(bigram_phraser[[tokens]], min_count=1, threshold=1)
    trigram_phraser = gensim.models.phrases.Phraser(trigram_model)

    # Lemmatizer
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in trigram_phraser[bigram_phraser[tokens]]]

    return tokens

analyzer = SentimentIntensityAnalyzer()

def write_to_csv_and_send_to_es(record):
    csv_file_path = "/app/transcription.csv"
    column_names = ["id", "timestamp", "text", "duration", "summary"]

    is_empty = os.stat(csv_file_path).st_size == 0

    if is_empty:
        # If the CSV file is empty, add a new row with initial data
        initial_data = ["2023-11-22T17:01:59", "2023-11-22T17:01:59", "PARL: Process Analysis Real Time Language Application", 20.01018359107971, "A.A. 2022/2023"]
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
        writer.writerow([record['id'], record['timestamp'], record['text'], record['duration'], record['summary']])

    processed_ids.add(record['id'])

    # Translate to en
    translator = Translator()

    dataset = pd.read_csv(csv_file_path)

    np.random.seed(42)

    results = []

    dominant_topics = []
    dominant_topic_percentages = []
    topic_keywords = []

    print("Finding topic...")

    # Prendi solo l'ultima riga del dataset
    row = dataset.iloc[-1]
    result_words = []

    tokens = preprocess_text(row['text'])

    # Corpus
    id2word = corpora.Dictionary([tokens])
    corpus = [id2word.doc2bow(tokens)]

    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=id2word, num_topics=10, random_state=100, update_every=1, chunksize=100, passes=10, alpha="auto", per_word_topics=True)

    topics = lda_model.print_topics()

    unique_words = set()

    coherence_model_lda = CoherenceModel(model=lda_model, texts=[tokens], dictionary=id2word, coherence='c_v')
    coherence_lda = coherence_model_lda.get_coherence()

    topic_scores = sorted(lda_model.get_document_topics(corpus[0], minimum_probability=0), key=itemgetter(1), reverse=True)

    dominant_topic, dominant_topic_percentage = topic_scores[0]

    topic_keywords = [word for word, _ in lda_model.show_topic(dominant_topic)]

    dominant_topics = [dominant_topic]
    dominant_topic_percentages = [dominant_topic_percentage]

    # Detect language for VADER, because it works better with en
    detected_language = detect(record['text'])
    if detected_language != 'en':
        # If the detected language is not English, translate the text
        translation = translator.translate(record['text'], dest='en').text
    else:
        # If the detected language is already English, use the original text
        translation = record['text']

    # Sentiment
    sentiment_score = analyzer.polarity_scores(translation)

    # Check sentiment score range
    sentiment_text = get_sentiment_text(sentiment_score['compound'])

    results.append({
        'ID': row['id'],
        'Topic': dominant_topics,
        'Topic Score': dominant_topic_percentages,
        'Top Terms': topic_keywords,
        "Sentiment Score" : sentiment_score,
        "Sentiment Text": sentiment_text,
    })
    print("Done!")

    es_data = {
        "id": record['id'],
        "timestamp": record['timestamp'],
        "text": record['text'],
        "summary": record['summary'],
        "duration": record['duration'],
        "topic":dominant_topics,
        "topic_score":dominant_topic_percentages,
        "top_terms": topic_keywords,
        "sentiment_score" : sentiment_score,
        "sentiment_text": sentiment_text,
    }
    es.index(index=elastic_index, body=es_data, ignore=400)

    print("Send data to es!")

def get_sentiment_text(compound_score):
    if compound_score >= 0.8:
        return "Estremamente positivo"
    elif 0.6 <= compound_score < 0.8:
        return "Molto positivo"
    elif 0.4 <= compound_score < 0.6:
        return "Moderatamente positivo"
    elif 0.2 <= compound_score < 0.4:
        return "Leggermente positivo"
    elif -0.2 < compound_score <= 0.2:
        return "Neutrale"
    elif -0.4 < compound_score <= -0.2:
        return "Leggermente negativo"
    elif -0.6 < compound_score <= -0.4:
        return "Moderatamente negativo"
    elif -0.8 < compound_score <= -0.6:
        return "Molto negativo"
    else:
        return "Estremamente negativo"

print("Reading from Kafka...")
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topic) \
    .load()

df = df.selectExpr("CAST(value AS STRING)")
df = df.select(from_json("value", schema).alias("data"))
df = df.select("data.id", "data.timestamp", "data.text", "data.duration", "data.summary")

print("Saving to CSV and sending to Elasticsearch...")
df.writeStream \
    .foreach(write_to_csv_and_send_to_es) \
    .start() \
    .awaitTermination()
