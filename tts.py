import pyttsx3

def talk(text):
    """Removes asterisks from the text and then speaks it."""
    # Filter out the asterisks
    text_to_speak = text.replace('*', '')
    
    engine = pyttsx3.init()
    engine.say(text_to_speak)
    engine.runAndWait()
