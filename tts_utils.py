import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

def speak(text, lang='en'):
    if lang == 'es':
        # Select Spanish voice (change index according to your system)
        engine.setProperty('voice', voices[0].id)
    else:
        # Default English voice
        engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()
