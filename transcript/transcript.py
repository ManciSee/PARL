import io
import speech_recognition as sr
import time
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

recording = False
transcription_data = []  # Lista per memorizzare le trascrizioni

@app.route('/')
def index():
    return render_template('index.html', recording=recording)

@app.route('/start')
def start_recording():
    id_recording = 0
    global recording
    recording = True

    r = sr.Recognizer()
    mic = sr.Microphone(device_index=0)

    with mic as source:
        r.adjust_for_ambient_noise(source)
        print("Inizio registrazione...")

        while recording:
            audio = r.listen(source)
            try:
                start_time = time.time()
                transcription = r.recognize_whisper(audio, "small", False, None, "it", False)
                end_time = time.time()
                transcription_duration = end_time - start_time

                print("Hai detto:", transcription)

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                stream = {
                    'id': id_recording,
                    'timestamp': timestamp,
                    'text': transcription,
                    'duration': transcription_duration
                }
                id_recording += 1

                transcription_data.append(stream)

                for stream in transcription_data:
                    data = {
                        'id': stream['id'],
                        'timestamp': stream['timestamp'],
                        'text': stream['text'],
                        'duration': stream['duration']
                    }
                    headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
                    url = 'http://localhost:9090'
                    response = requests.post(url, data=json.dumps(data), headers=headers)

            except sr.UnknownValueError:
                print("Nessun input vocale rilevato.")
            except sr.RequestError as e:
                print("Errore di connessione al servizio di riconoscimento vocale: {0}".format(e))

    return "Registrazione interrotta. Trascrizione salvata in 'transcription.json'."

@app.route('/stop')
def stop_recording():
    global recording
    recording = False
    return "Registrazione interrotta. Trascrizione salvata in 'transcription.json'."

@app.route('/upload', methods=['POST'])
def upload_file():
    id_audio = 0
    global recording
    recording = False

    if 'file' not in request.files:
        return "Nessun file selezionato"

    file = request.files['file']
    if file.filename == '':
        return "Nome file vuoto"

    if file:
        audio_data = file.read()

        # Imposta la larghezza dei campioni a 2 (16 bit)
        sample_width = 2
        sample_rate = 44100  # Assumendo un campionamento a 44.1 kHz

        r = sr.Recognizer()
        audio = sr.AudioData(audio_data, sample_rate=sample_rate, sample_width=sample_width)

        try:
            start_time = time.time()
            transcription = r.recognize_whisper(audio, "small", False, None, "it", False)
            end_time = time.time()
            transcription_duration = end_time - start_time

            print("Trascrizione del file audio:")
            print(transcription)
            print("Durata della trascrizione: {} secondi".format(transcription_duration))

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            stream = {
                    'id': id_audio,
                    'timestamp': timestamp,
                    'text': transcription,
                    'duration': transcription_duration
                }
            id_audio += 1

            transcription_data.append(response)

            for stream in transcription_data:
                data = {
                    'id': stream['id'],
                    'timestamp': stream['timestamp'],
                    'text': stream['text'],
                    'duration': stream['duration']
                }
                headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
                url = 'http://localhost:9090'
                response = requests.post(url, data=json.dumps(data), headers=headers)

            # Salva i dati in un file JSON
            # with open("transcription.json", "a") as output:
            #     json.dump(transcription_data, output, indent=2)

        except sr.UnknownValueError:
            return "Nessun input vocale rilevato."
        except sr.RequestError as e:
            return "Errore di connessione al servizio di riconoscimento vocale: {0}".format(e)


@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    return jsonify(transcription_data)

if __name__ == '__main__':
    app.run(port=8880, debug=True)
