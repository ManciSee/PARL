import io
import speech_recognition as sr
import time
import json
import wave
import requests  # Aggiunto il modulo requests
from flask import Flask, render_template, request

app = Flask(__name__)

recording = False

@app.route('/')
def index():
    return render_template('index.html', recording=recording)

@app.route('/start')
def start_recording():
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
                transcription = r.recognize_whisper(audio, "medium", False, None, "it", False)
                end_time = time.time()
                transcription_duration = end_time - start_time

                print("Hai detto:", transcription)

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                response = {
                    "transcription": []
                }
                response["transcription"].append({"timestamp": timestamp, "text": transcription, "duration": transcription_duration})

                with open("transcription.json", "w") as output:
                    json.dump(response, output, indent=2)

                # Invia i dati a Fluent Bit sulla porta 9090
                fluent_bit_url = 'http://fluent-bit:9090'  # Assumi che Fluent Bit sia in esecuzione sullo stesso host
                try:
                    response = requests.post(fluent_bit_url, json=response)
                    if response.status_code == 200:
                        print("Dati inviati con successo a Fluent Bit.")
                    else:
                        print(f"Errore nell'invio dei dati a Fluent Bit. Risposta: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f'Errore nell\'invio dei dati a Fluent Bit: {e}')

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
            transcription = r.recognize_whisper(audio, "medium", False, None, "it", False)
            end_time = time.time()
            transcription_duration = end_time - start_time

            print("Trascrizione del file audio:")
            print(transcription)
            print("Durata della trascrizione: {} secondi".format(transcription_duration))

            # Apri il file JSON esistente e carica i dati
            with open("transcription.json", "r") as input:
                existing_data = json.load(input)
            
            # Aggiungi la nuova trascrizione ai dati esistenti
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            response = {
                "transcription": []
            }
            response["transcription"].append({"timestamp": timestamp, "text": transcription, "duration": transcription_duration})
            existing_data["transcription"].append({"timestamp": timestamp, "text": transcription, "duration": transcription_duration})
            
            # Salva i dati aggiornati nel file JSON
            with open("transcription.json", "w") as output:
                json.dump(existing_data, output, indent=2)

            # Invia i dati a Fluent Bit sulla porta 9090
            fluent_bit_url = 'http://fluent-bit:9090'  # Assumi che Fluent Bit sia in esecuzione sullo stesso host
            try:
                response = requests.post(fluent_bit_url, json=existing_data)
                if response.status_code == 200:
                    print("Dati inviati con successo a Fluent Bit.")
                else:
                    print(f"Errore nell'invio dei dati a Fluent Bit. Risposta: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f'Errore nell\'invio dei dati a Fluent Bit: {e}')

            return transcription
        except sr.UnknownValueError:
            return "Nessun input vocale rilevato."
        except sr.RequestError as e:
            return "Errore di connessione al servizio di riconoscimento vocale: {0}".format(e)

if __name__ == '__main__':
    app.run(port=8880, debug=True)
