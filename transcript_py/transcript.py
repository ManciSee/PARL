# import speech_recognition as sr

# r = sr.Recognizer()

# mic = sr.Microphone()

# with mic as source:
#     r.adjust_for_ambient_noise(source) 
#     audio = r.listen(source)
#     print("Trascrizione: " + r.recognize_google(audio, language="it-IT"))

# import speech_recognition as sr

# r = sr.Recognizer()
# mic = sr.Microphone()

# with mic as source:
#     r.adjust_for_ambient_noise(source)

#     print("In ascolto...")

#     while True:
#         audio = r.listen(source)

#         try:
#             transcription = r.recognize_google(audio, language="it-IT")
#             print("Trascrizione in tempo reale:", transcription)
#         except sr.UnknownValueError:
#             print("Nessun audio rilevato.")
#         except sr.RequestError as e:
#             print(f"Errore nella richiesta di riconoscimento vocale: {e}")


import speech_recognition as sr

def recognize(recognizer, microphone):
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    response = {
        "success" : True,
        "error" : None, 
        "transcription" : None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"
    
    return response

if __name__ == "__main__":
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()