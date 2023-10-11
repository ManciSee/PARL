import speech_recognition as sr
import time
import json

r = sr.Recognizer()
mic = sr.Microphone(device_index=0)
timeout = 10
timeout_start = time.time()

response = {
    "transcription": []
}

with mic as source:
    r.adjust_for_ambient_noise(source)
    print("In ascolto...")

    while time.time() < timeout_start + timeout:
        audio = r.listen(source)
        try:
            start_time = time.time()  
            transcription = r.recognize_whisper(audio, "tiny", False, None, "it", False)
            end_time = time.time()  
            transcription_duration = end_time - start_time  

            print("Hai detto:", transcription)
            print("Durata della trascrizione: {} secondi".format(transcription_duration))

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            response["transcription"].append({"timestamp": timestamp, "text": transcription, "duration": transcription_duration})

            
            with open("transcription.json", "w") as output:
                json.dump(response, output, indent=2)

            print("Risposta:", response)
        except sr.UnknownValueError:
            print("Nessun input vocale rilevato.")
        except sr.RequestError as e:
            print("Errore di connessione al servizio di riconoscimento vocale: {0}".format(e))

    print("Rilevamento terminato. Trascrizione salvata in 'transcription.json'")
