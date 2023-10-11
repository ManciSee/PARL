
import speech_recognition as sr
import time

r = sr.Recognizer()
mic = sr.Microphone(device_index=0)
timeout = 10
timeout_start = time.time()
print(sr.Microphone.list_microphone_names())

response = {
    "success": True,
    "error": None,
    "transcription": None
}

with mic as source:
    r.adjust_for_ambient_noise(source)
    print("In ascolto...")

    while time.time() < timeout_start + timeout:
        audio = r.listen(source)

        try:
            transcription = r.recognize_google(audio, language="it-IT")
            print("Hai detto:", transcription)
            response["transcription"] = transcription

            # Salvataggio della trascrizione in un file di testo
            with open("trascrizione.txt", "a") as file:
                file.write(transcription + "\n")
        except sr.RequestError:
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech"

print("Risposta:", response)
