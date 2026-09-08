# opens web services such as youtube google and instagram

import webbrowser

class WebService:

    def handle(self, command):

        if "open google" in command:
            webbrowser.open("https://google.com")
            return True

        if "open instagram" in command:
            webbrowser.open("https://instagram.com")
            return True

        if "open youtube" in command:
            webbrowser.open("https://youtube.com")
            return True

        return False