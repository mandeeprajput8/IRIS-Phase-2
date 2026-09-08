"""
Project Iris (Aurora Core)
A Modular AI Assistant Backend

Designed and Built by Mandeep Singh
Phase 1 Completed: 1st March, 2026

This project was architected with layered design principles,
persistent MySQL memory, and LLM-based contextual reasoning.
"""

from core.iris import run
from voice.tts import speak

if __name__ == "__main__":
    print("Booting Aurora core...\n\nDesigned by Mandeep Singh")
    speak("\nInitialising Iris...")
    run()
    