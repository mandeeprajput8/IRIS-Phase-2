# central router for local commands

class CommandRouter:

    def __init__(self, spotify_services, web_services):
        self.spotify = spotify_services
        self.web = web_services

    def route(self, command):
        command = command.lower()

        if command.startswith("play"):
            return self.spotify.handle(command)

        if "open" in command: # open "name of site"
            return self.web.handle(command)

        return False