import pyttsx3
import asyncio
import edge_tts
# converts text-to-speech

# ==== ONLINE VOCIE ====

async def speak_online(text):
    try:
        communicate = edge_tts.Communicate(
            text,
            voice="en-IE-EmilyNeural",
            rate="-8%",
            pitch="+1Hz"
        )

        # Stream audio directly to mpv (no file saving, no delay)
        process = await asyncio.create_subprocess_exec(
            "mpv",
            "--no-terminal",
            "--quiet",
            "--no-cache",
            "--audio-buffer=0.1",
            "fd://0",
            stdin=asyncio.subprocess.PIPE
        )

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                process.stdin.write(chunk["data"])
                await process.stdin.drain()

        process.stdin.close()
        try:
            await process.wait()
        except asyncio.CancelledError:
            process.kill()
            await process.wait()
            
    except asyncio.CancelledError:
        pass



# ==== OFFLINE FALLBACK ====
'''
Reinitialize engine each call to avoid Windows SAPI5 event-loop deadlock (first speak working, the second one, not)
observed after runAndWait() when mic is reused
The issue was caused by a library-level event loop deadlock in pyttsx3 on Windows, not by the Python interpreter or application logic'''

# def speak_offline(text):
#     engine = pyttsx3.init('sapi5') # provides male and female voices in windows
#     voices = engine.getProperty('voices')
#     engine.setProperty('voice', voices[1].id)  # Index 0 for male & 1 for female voice   
#     engine.setProperty('rate', 155)
#     engine.setProperty('volume', 0.9)
#     engine.say(text)
#     engine.runAndWait()
#     engine.stop()

def speak(text):
    try:
        asyncio.run(speak_online(text))
    except Exception:
        print("Online TTS failed. Switching to offline mode.")
        
