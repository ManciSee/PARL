import speech_recognition as sr
import time
import json
from flask import Flask, render_template

app = Flask(__name__)

response = {
    "transcription": []
}

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
                response["transcription"].append({"timestamp": timestamp, "text": transcription, "duration": transcription_duration})

                with open("transcription.json", "w") as output:
                    json.dump(response, output, indent=2)

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

if __name__ == '__main__':
    app.run(debug=True)
