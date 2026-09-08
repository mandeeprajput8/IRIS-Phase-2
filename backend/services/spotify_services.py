import webbrowser
from voice.tts import speak
from services.musicLibrary import music

class SpotifyService:

    def handle(self, command):

        song = command.split("play", 1)[1].strip()

        # adding a failsafe in case the song is not there is the musicLib
        print(f"Extracted song: '{song}'")

        if song in music:
            link = music[song]
            webbrowser.open(link)
            speak(f"Playing: {song}")
        else:
            speak("Sorry, could not find the song you are looking for.")

        return True