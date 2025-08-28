import pyttsx3

try:
    engine = pyttsx3.init()
except Exception as e:
    print(f"Failed to initialize TTS engine: {e}")
    engine = None

def talk(text_to_speak):
    """
    Speaks the given text using the pre-initialized pyttsx3 engine.
    This is a blocking function.
    """
    if not engine:
        print("TTS engine is not available.")
        return

    try:
        engine.say(text_to_speak)
        engine.runAndWait()
    except Exception as e:
        print(f"An error occurred during TTS playback: {e}")