from core.iris import Iris


class IrisService:

    def __init__(self):
        self.iris = Iris()

    def process_chat(self, message: str):
        return self.iris.process_command(message)

    def process_command(self, command: str):
        return self.iris.process_command(command)

    def is_database_connected(self):
        return self.iris.memory.is_database_connected()


# ============================================================
# SHARED IRIS SERVICE
# ============================================================
# Create ONE IrisService instance for the entire backend.
#
# This means:
#
# IrisService
#      ↓
#    Iris
#      ↓
#   Memory
#      ↓
# MySQL connection
#
# Chat, Command, Voice and Health will all use this
# same instance instead of creating their own.
# ============================================================

iris_service = IrisService()