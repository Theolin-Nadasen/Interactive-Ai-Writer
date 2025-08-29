
import pyttsx3
import re

def find_voices(engine):
    """Scans the system for available voices and prints their properties."""
    voices = engine.getProperty('voices')
    male_voice_id = None
    female_voice_id = None

    print("---" + " Available Voices ---")
    for voice in voices:
        print(f"ID: {voice.id}")
        print(f"  Name: {voice.name}")
        print(f"  Age: {voice.age}")
        print(f"  Gender: {voice.gender}")
        print(f"  Lang: {voice.languages}")
        print("-" * 20)

    # First pass: Check for the 'gender' attribute
    for voice in voices:
        if not male_voice_id and hasattr(voice, 'gender') and voice.gender == 'male':
            male_voice_id = voice.id
        if not female_voice_id and hasattr(voice, 'gender') and voice.gender == 'female':
            female_voice_id = voice.id
        if male_voice_id and female_voice_id:
            break

    # Fallback: If gender attribute isn't available, check for common names
    if not male_voice_id or not female_voice_id:
        for voice in voices:
            name = voice.name.lower()
            if not male_voice_id and any(n in name for n in ['david', 'mark', 'james', 'microsoft david']):
                male_voice_id = voice.id
            if not female_voice_id and any(n in name for n in ['zira', 'hazel', 'susan', 'microsoft zira']):
                female_voice_id = voice.id

    # If a specific gender is not found, use the first and second voice as stand-ins
    if not male_voice_id and len(voices) > 0: male_voice_id = voices[0].id
    if not female_voice_id and len(voices) > 1: female_voice_id = voices[1].id
    
    print(f"\n---" + " Detected Voices ---")
    print(f"Male voice ID: {male_voice_id}")
    print(f"Female voice ID: {female_voice_id}")
    print("-" * 20)
    
    return male_voice_id, female_voice_id


def talk(text_with_tags):
    """
    Parses a string with special tags to control voice properties.
    """
    engine = pyttsx3.init()

    default_rate = engine.getProperty('rate')
    default_volume = engine.getProperty('volume')
    default_voice_id = engine.getProperty('voice')

    male_voice_id, female_voice_id = find_voices(engine)

    pattern = r'(<rate=\d+>|<volume=\d\.\d+>|<voice=male>|<voice=female>|<voice=default>|<default>)'
    parts = re.split(pattern, text_with_tags)
    parts = [part for part in parts if part]

    for part in parts:
        if part.startswith('<rate='):
            try:
                engine.setProperty('rate', int(part.strip('<>').split('=')[1]))
            except (ValueError, IndexError): pass

        elif part.startswith('<volume='):
            try:
                engine.setProperty('volume', float(part.strip('<>').split('=')[1]))
            except (ValueError, IndexError): pass

        elif part == '<voice=male>':
            if male_voice_id:
                print("\nSwitching to male voice...")
                engine.setProperty('voice', male_voice_id)

        elif part == '<voice=female>':
            if female_voice_id:
                print("\nSwitching to female voice...")
                engine.setProperty('voice', female_voice_id)
        
        elif part == '<voice=default>':
            print("\nSwitching to default voice...")
            engine.setProperty('voice', default_voice_id)

        elif part == '<default>':
            engine.setProperty('rate', default_rate)
            engine.setProperty('volume', default_volume)

        else:
            engine.say(part)
    
    engine.runAndWait()

if __name__ == '__main__':
    print("Running TTS debug script...")
    talk("This is the default voice. <voice=male> This should be a male voice. <voice=female> This should be a female voice.")
