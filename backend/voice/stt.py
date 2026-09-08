# converts speech-to-text
import speech_recognition as sr
r = sr.Recognizer()

def listen(timeout=4, phrase_time_limit=5):
    # recognize speech using recognize_google
    ''' 
    NOTE: recognize_google() requires internet to interpret what the user is saying as it relies on googles web speech API, which processes audio on google's server
    '''

    try:
        with sr.Microphone() as source:
            # this part basically tells us how much delay there is 
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5) # adjusts the bg noise
            
            # lets the user think for 1.5sec before recording stops
            r.pause_threshold = 1.5 
            r.non_speaking_duration = 0.5

            audio = r.listen(
                source, 
                timeout=4, 
                phrase_time_limit=5)
                # hover over r.listen to understand what timeout and phrase_time_limit means
                
        word = r.recognize_google(audio) # converts speech to text
        print(f"Your command: {word}")
        return word
        
    except sr.WaitTimeoutError:
        print("Listening timed out.")
        return None

    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None

    except sr.RequestError as e:
        print(f"API unavailable: {e}")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


'''NOTE
Future update is to completely remove recognize_google and replace it with faster-whisper, already installed supporting packages


'''

