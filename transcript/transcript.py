import io
import speech_recognition as sr
import time
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
recording = False
transcription_data = []  # Lista per memorizzare le trascrizioni

@app.route('/')
def index():
    return render_template('index.html', recording=recording)


@app.route('/sendRecording', methods=['POST'])
def get_recording():
    data = request.json
    # Ora puoi accedere al campo 'text' all'interno del JSON
    transcription = data['text']
    duration = data['duration']
    if transcription:  # Verifica se la trascrizione non è vuota
        print("Hai detto:", transcription)

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

        stream = {
            'id': timestamp,
            'timestamp': timestamp,
            'text': transcription,
            'duration': duration
        }
        #id_recording += 1
        # transcription_data=[]
        transcription_data.append(stream)

        # for stream in transcription_data:
        # data = {
        #         'id': stream['id'],
        #         'timestamp': stream['timestamp'],
        #         'text': stream['text'],
        #         'duration': stream['duration']
        # }
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        #url = 'http://localhost:9090'
        url = "https://192.168.66.231:9090"
        response = requests.post(url, data=json.dumps(stream), headers=headers)
    return json.dumps("{ok:true}")
    # id_recording = 0
    # global recording
    # recording = True
    # print()
    # r = sr.Recognizer()
    # mic = sr.Microphone(device_index=0)

    # with mic as source:
    #     r.adjust_for_ambient_noise(source)
    #     print("Inizio registrazione...")

    #     while recording:
    #         audio = r.listen(source)
    #         try:
    #             start_time = time.time()
    #             transcription = r.recognize_whisper(audio, "small", False, None, "it", False)
    #             end_time = time.time()
    #             transcription_duration = end_time - start_time

    #             if transcription:  # Verifica se la trascrizione non è vuota
    #                 print("Hai detto:", transcription)

    #                 timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

    #                 stream = {
    #                     'id': id_recording,
    #                     'timestamp': timestamp,
    #                     'text': transcription,
    #                     'duration': transcription_duration
    #                 }
    #                 id_recording += 1
    #                 # transcription_data=[]
    #                 transcription_data.append(stream)

    #                 # for stream in transcription_data:
    #                 # data = {
    #                 #         'id': stream['id'],
    #                 #         'timestamp': stream['timestamp'],
    #                 #         'text': stream['text'],
    #                 #         'duration': stream['duration']
    #                 # }
    #                 headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    #                 url = 'http://localhost:9090'
    #                 response = requests.post(url, data=json.dumps(stream), headers=headers)

    #         except sr.UnknownValueError:
    #             print("Nessun input vocale rilevato.")
    #         except sr.RequestError as e:
    #             print("Errore di connessione al servizio di riconoscimento vocale: {0}".format(e))

    # return "Registrazione interrotta. Trascrizione salvata in 'transcription.json'."


# @app.route('/stop')
# def stop_recording():
#     global recording
#     recording = False
#     return "Registrazione interrotta. Trascrizione salvata in 'transcription.json'."

@app.route('/upload', methods=['POST'])
def upload_file():
    id_audio = 0
    global recording
    recording = False
    response = None

    if 'file' not in request.files:
        return "Nessun file selezionato"

    file = request.files['file']
    if file.filename == '':
        return "Nome file vuoto"

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
            
            # tiny.en much faster for English text
            recognized_text = r.recognize_whisper(audio, "tiny.en", False, None, "en", False)
            end_time = time.time()  

            transcription_duration = end_time - start_time

            print("Testo riconosciuto:")
            print(recognized_text)
            print("Durata della trascrizione: {} secondi".format(transcription_duration))
            print("Elaborazione completata.")
            
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
            stream = {
                    'id': timestamp,
                    'timestamp': timestamp,
                    'text': recognized_text,
                    'duration': transcription_duration
                }
            id_audio += 1

            transcription_data.append(stream)
            for stream in transcription_data:
                data = {
                    'id': stream['id'],
                    'timestamp': stream['timestamp'],
                    'text': stream['text'],
                    'duration': stream['duration']
                }
                headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
                #url = 'http://localhost:9090'
                url = "https://192.168.66.231:9090"
                response = requests.post(url, data=json.dumps(data), headers=headers)
    return json.dumps(data)


@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    return jsonify(transcription_data)

if __name__ == '__main__':
    app.run(host="192.168.66.231",port=8880, debug=True, ssl_context='adhoc')
