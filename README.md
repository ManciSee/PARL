# PARL: Process Analysis Real Time Language Application
<p align="center">
<img src="./images/Parlogo.png" style="width:40%; height:40%;">
</p>

This project constitutes my bachelor's thesis in Computer Science at the University of Catania. "PARL" is an innovative solution aimed at enhancing the experience of speakers and listeners through real-time Speech to Text and advanced analysis of audio files. Implemented on a containerized distributed architecture with Docker, the platform leverages open-source technologies such as Kafka, Spark, Fluent Bit, Elasticsearch, and Kibana to optimize the process.

"PARL" offers advanced features, including real-time Speech to Text with high accuracy, Topic Modeling, Sentiment Analysis, and Text Summarization. Targeted at a diverse audience, including professionals in the audiovisual industry, journalists, academic researchers, and businesses, the project promises to significantly improve the experience by utilizing stream processing tools. These tools enable real-time processing of audio signals and the execution of operations for text comprehension and analysis, opening new opportunities for semantic and sentiment analysis in the field of information and communication.
## ℹ️ How to use
1. Clone the repository
```bash
git clone https://github.com/ManciSee/PARL.git
cd folder_name
```
2. Install the requirements that are inside the ```transcript``` folder
```bash
cd transcript
pip install -r requirements.txt
```
3. Build and run the docker container
 ```bash
cd folder_name
docker compose-up -d
```
5. Run the Flask server
```bash
cd transcript
python3 transcript.py
```
6. Start the recording or upload the WAV file
7. Enjoy!
## ⚠️ Disclaimer
if the ```docker compose``` doesn't work, run the container in this order:
1. Zookeper
2. Kafka
3. Fluent Bit
4. Elasticsearch
5. Spark
6. Kibana
## 🎙️ Demo

## 👥 License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
