import os
from decouple import config
from langchain.llms import Replicate
import re

REPLICATE_API_TOKEN = config('REPLICATE_API_TOKEN')
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

llm: Replicate = Replicate(
    #model = "meta/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1",
    model = "meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d",
    model_kwargs = {"temperature":0.80, "max_lenght":500, "top_p":1}
)


# prompt: str = """
# Human: Make a simple summarize of this text: "Volunteering in the community is a fulfilling way to make a positive impact. Whether it's helping at a local shelter or participating in environmental initiatives, small actions can create meaningful change."
# AI
# """

# prompt: str = """
# [INST] Give me 3 topics of this text "Sharing laughter with others creates a sense of connection and joy. What's a funny story or joke that always brings a smile to your face?". write only the topics, without number and without other text, only the topics [/INST]
# """

prompt: str = """
[INST]
    Give me 3 topics of this text, only the topics : "Sharing laughter with others creates a sense of connection and joy. What's a funny story or joke that always brings a smile to your face?".
[/INST]
"""


response: str = llm(prompt=prompt)
print(response)






# ---- WORKING ----
# import os
# import csv
# import pandas as pd
# from decouple import config
# from langchain.llms import Replicate

# REPLICATE_API_TOKEN = config('REPLICATE_API_TOKEN')
# os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# llm: Replicate = Replicate(
#     model="meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d",
#     model_kwargs={"temperature": 0.80, "max_length": 500, "top_p": 1}
# )

# # Read the content of the CSV file
# csv_file_path = "prova.csv"  # Update this with the correct path

# # Load CSV into a DataFrame
# df = pd.read_csv(csv_file_path, encoding='utf-8')

# # Create a new column for topics
# df['topic'] = ''

# for index, row in df.iterrows():
#     # Extract values from the current row
#     row_id = row['id']
#     text = row['text']

#     # Build the prompt for the current row
#     prompt = f"""
#     {text} Give me 3 topics of this text. Write only the topics, without number and without other text, only the topics {text}
#     """

#     # Get the response from the language model
#     response = llm(prompt=prompt)

#     # Extract topics and update the 'topic' column
#     topics = response.split('\n')[:3]  # Assuming the topics are in the first three lines of the response
#     df.at[index, 'topic'] = ', '.join(topics)

# # Save the updated DataFrame to a new CSV file
# df.to_csv("transcription_with_topics.csv", index=False, encoding='utf-8')

# # Print the DataFrame
# print(df)
# ---------------------------------------------------------------