import io
import speech_recognition as sr
import time
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from summarizer import Summarizer

app = Flask(__name__)
CORS(app)
recording = False
transcription_data = []  

@app.route('/')
def index():
    return render_template('index.html', recording=recording)


@app.route('/sendRecording', methods=['POST'])
def get_recording():
    data = request.json
    transcription = data['text']
    duration = data['duration']
    if transcription:
        print("Hai detto:", transcription)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

        stream = {
            'id': timestamp,
            'timestamp': timestamp,
            'text': transcription,
            'duration': duration
        }
        transcription_data.append(stream)

        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        #url = 'http://localhost:9090'
        url = "http://192.168.66.231:9090"
        response = requests.post(url, data=json.dumps(stream), headers=headers)
    return json.dumps("{ok:true}")

# @app.route('/stop')
# def stop_recording():
#     global recording
#     recording = False
#     return "Registrazione interrotta. Trascrizione salvata in 'transcription.json'."

@app.route('/upload', methods=['POST'])
def upload_file():
    global recording
    recording = False
    response = None

    if 'file' not in request.files:
        return "Nessun file selezionato"

    file = request.files['file']
    if file.filename == '':
        return "Nome file vuoto"

    # Text summarizer
    model_name = 'distilbert-base-uncased'
    model = Summarizer(model_name)

    if file:
        audio_data = io.BytesIO(file.read())
        r = sr.Recognizer()
        audio = sr.AudioFile(audio_data)

        with audio as source:
            print("Rilevamento del livello di rumore ambientale...")
            r.adjust_for_ambient_noise(source, 0.5)
            print("Livello di rumore ambientale rilevato e adattato.")
            audio = r.record(source)

            print("Avvio del riconoscimento vocale...")

            start_time = time.time()            
            # recognized_text = r.recognize_whisper(audio, "medium", False, None, None, False)
            recognized_text = r.recognize_whisper(audio, "small", False, None, None, False)
            end_time = time.time()  

            transcription_duration = end_time - start_time

            print("Testo riconosciuto:")
            print(recognized_text)
            print("Durata della trascrizione: {} secondi".format(transcription_duration))
            print("Elaborazione completata.")
            
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

            # summary
            optimal_k = model.calculate_optimal_k(recognized_text, k_max=10)
            result = model(recognized_text, min_length=100, num_sentences=optimal_k)
            summary = ''.join(result)

            streams = {
                    'id': timestamp,
                    'timestamp': timestamp,
                    'text': recognized_text,
                    'duration': transcription_duration,
                    'summary' : summary
                }
            headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
            #url = 'http://localhost:9090'
            url = "http://192.168.66.231:9090"
            response = requests.post(url, data=json.dumps(streams), headers=headers)
    return json.dumps(streams)


@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    return jsonify(transcription_data)

if __name__ == '__main__':
    app.run(host="192.168.66.231",port=8880, debug=True, ssl_context='adhoc')