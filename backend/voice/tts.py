import asyncio
import edge_tts
# converts text-to-speech

# ==== ONLINE VOICE ====

VOICE_CANDIDATES = (
    "en-GB-SoniaNeural",
    "en-GB-LibbyNeural",
    "en-US-EmmaMultilingualNeural",
    "en-US-JennyNeural",
)


async def _stream_voice_to_mpv(text, voice):
    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate="-8%",
        pitch="+1Hz"
    )

    process = None
    try:
        async for chunk in communicate.stream():
            if chunk["type"] != "audio":
                continue

            if process is None:
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

            process.stdin.write(chunk["data"])
            await process.stdin.drain()

        if process is None:
            raise RuntimeError(f"No audio chunks received for voice {voice}")

        if process.stdin and not process.stdin.is_closing():
            process.stdin.close()

        await process.wait()

        if process.returncode != 0:
            raise RuntimeError(f"mpv exited with code {process.returncode}")

    except asyncio.CancelledError:
        if process and process.returncode is None:
            process.kill()
            await process.wait()
        raise
    except Exception:
        if process and process.returncode is None:
            process.kill()
            await process.wait()
        raise


async def speak_online(text):
    if not text or not text.strip():
        return

    last_error = None
    for voice in VOICE_CANDIDATES:
        try:
            await _stream_voice_to_mpv(text, voice)
            return
        except asyncio.CancelledError:
            return
        except Exception as e:
            last_error = e
            print(f"Voice {voice} failed ({e}), trying next voice...")

    if last_error is not None:
        raise last_error


# ==== OFFLINE FALLBACK (disabled for Phase 2) ====
'''
Reinitialize engine each call to avoid Windows SAPI5 event-loop deadlock (first speak working, the second one, not)
observed after runAndWait() when mic is reused
The issue was caused by a library-level event loop deadlock in pyttsx3 on Windows, not by the Python interpreter or application logic'''

# import pyttsx3
#
# def speak_offline(text):
#     engine = pyttsx3.init('sapi5') # provides male and female voices in windows
#     voices = engine.getProperty('voices')
#     if voices:
#         voice_index = 1 if len(voices) > 1 else 0
#         engine.setProperty('voice', voices[voice_index].id)  # Index 0 for male & 1 for female voice
#     engine.setProperty('rate', 155)
#     engine.setProperty('volume', 0.9)
#     engine.say(text)
#     engine.runAndWait()
#     engine.stop()

def speak(text):
    try:
        asyncio.run(speak_online(text))
    except Exception as e:
        print(f"Online TTS failed ({e}).")
