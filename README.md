# PARL: Processing Analysis Real Time Language Application
<p align="center">
<img src="./images/Parlogo.png" style="width:40%; height:40%;">
</p>

This thesis represents my bachelor’s project in Computer Science at the University of Catania, focusing on the TAP course taught by Professor Salvatore Nicotra. “PARL” is an innovative solution aimed at enhancing the experience of speakers and listeners through real-time Speech to Text and advanced analysis of audio files. Implemented on a containerized distributed architecture with Docker, the platform leverages open-source technologies such as Kafka, Spark, Fluent Bit, Elasticsearch, and Kibana to optimize the process.

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
6. Open the server on the port ```8880```
7. Before starting the recording, choose the correct language in the html file or upload the WAV file
8. Enjoy!
## ⚠️ Disclaimer 
If the ```docker compose``` doesn't work, run the container in this order:
1. Zookeper
2. Kafka
3. Fluent Bit
4. Elasticsearch
5. Spark
6. Kibana
<br/> 

If your browser doesn't support the [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition), change the browser... Unfortunately at the moment only Google Chrome (not Brave or other) seems to be working at its best.

<br/> 
After downloading the repository, before being able to start everything, it is necessary to change the various ports and IP addresses of the server. In some files, sections of code for localhost have been commented.

## 🎙️ Demo
The first video demonstrates using the microphone for accurate voice transcriptions, while the second video showcases uploading a WAV file for a quick transcription. Both videos have been sped up for more efficient viewing. Remember to choose the appropriate Whisper model for your needs to optimize transcription based on your desired speed and accuracy.

https://github.com/ManciSee/PARL/assets/80248296/aebb1bf7-8e0f-492c-b6f0-0c4071396603 



https://github.com/ManciSee/PARL/assets/80248296/e354aa86-0944-4637-baa6-b2caae289e53





## 👥 License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
