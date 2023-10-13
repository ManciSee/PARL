import speech_recognition as sr
import time

r = sr.Recognizer()
audio = sr.AudioFile('./prova.wav')

with audio as source:
    print("Rilevamento del livello di rumore ambientale...")
    r.adjust_for_ambient_noise(source, 0.5)
    print("Livello di rumore ambientale rilevato e adattato.")
    audio = r.record(source)

    print("Avvio del riconoscimento vocale...")

    start_time = time.time()  

    recognized_text = r.recognize_whisper(audio, "tiny.en", False, None, "en", False)

    end_time = time.time()  
    transcription_duration = end_time - start_time

    print("Testo riconosciuto:")
    print(recognized_text)
    print("Durata della trascrizione: {} secondi".format(transcription_duration))
    print("Elaborazione completata.")
