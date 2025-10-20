import os
import time
import webbrowser
import logging
import threading
import sys
import speech_recognition as sr
import pyttsx3
from typing import Optional
import appManager

# local imports (assuming files are saved separately)
try:
    from clint import ask_ai, AIClientError
    import musicLibrary
except Exception:
    # If running as a single-file bundle, earlier sections provide implementations.
    pass


# --- Logger ---
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("Jarvis")


# --- TTS Engine setup ---
engine = pyttsx3.init("sapi5" if sys.platform.startswith("win") else None)
voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)


def speak(text: str, block: bool = True) -> None:
    """Speak text using the TTS engine and print it to console.
    - block=True waits until speaking ends.
    - block=False runs TTS in a background thread.
    """
    if not text:
        return
    print(f"Jarvis says: {text}")

    def _say():
        engine.say(text)
        engine.runAndWait()

    if block:
        _say()
    else:
        threading.Thread(target=_say, daemon=True).start()


# --- AI bridge ---


def aiProcess(command: str) -> str:
    """Send the user's command to AI and return reply text.
    Provides helpful error messages when the provider fails.
    """
    try:
        reply = ask_ai(command)
        return reply
    except NameError:
        # ask_ai not available because client_example.py not imported
        logger.warning("AI client not available; returning canned response.")
        return "AI client is not configured. Set OPENROUTER_API_KEY in environment to enable AI responses."
    except AIClientError as e:
        logger.error("AI client error: %s", e)
        return f"Sorry, I couldn't process that: {e}"
    except Exception as e:
        logger.exception("Unexpected error while contacting AI: %s", e)
        return "Sorry, something went wrong while talking to the AI."


# --- Command handling ---


def open_url(url: str) -> None:
    logger.info("Opening: %s", url)
    webbrowser.open(url)


def processCommand(command: str) -> None:
    c = (command or "").strip().lower()
    logger.info("Processing command: %s", c)

    if not c:
        speak("I didn't hear a command.")
        return

    # Quick mapping
    if "open google" in c:
        open_url("https://www.google.com")
        speak("Opening Google")
        return
    if "open youtube" in c:
        open_url("https://www.youtube.com")
        speak("Opening YouTube")
        return
    if "open linkedin" in c:
        open_url("https://www.linkedin.com")
        speak("Opening LinkedIn")
        return

    # Play command (supports multi-word song names)
    if c.startswith("play "):
        song = c[5:].strip()
        link = musicLibrary.get_link(song)
        if link:
            open_url(link)
            speak(f"Playing {song}")
        else:
            available = ", ".join(musicLibrary.list_songs().keys())
            speak(f"I couldn't find {song}. Available songs are: {available}")
        return

    # Open apps/files/folders via appManager
    if c.startswith("open "):
        target = c.replace("open ", "").strip()
        if appManager.open_item(target):
            speak(f"Opening {target}")
        else:
            speak(f"Sorry, I couldn't find {target}.")
        return
    
    # Otherwise fallback to AI
    speak("Thinking...")
    output = aiProcess(command)
    speak(output)


# --- Wake word loop ---


def listen_for_wakeword(recognizer: sr.Recognizer, mic: sr.Microphone) -> Optional[str]:
    """Listen briefly and return the recognized text (or None).

    This is a single attempt; the main loop manages retries and timing.
    """
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
        text = recognizer.recognize_google(audio)
        return text
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        logger.error("Speech recognition API error: %s", e)
        return None


def main_loop():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    speak("Initializing Jarvis...")
    try:
        while True:
            # Light pause so loop doesn't hog CPU
            time.sleep(0.1)
            logger.debug("Listening for wake word...")
            recognized = listen_for_wakeword(recognizer, mic)
            if not recognized:
                continue
            logger.info("Heard: %s", recognized)
            if recognized.strip().lower() == "jarvis":
                speak("Yes?")
                # Listen for the next command (longer phrase)
                try:
                    with mic as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
                    command = recognizer.recognize_google(audio)
                    logger.info("Command recognized: %s", command)
                    processCommand(command)
                except sr.WaitTimeoutError:
                    speak("I didn't hear anything. Say the command after calling my name.")
                except sr.UnknownValueError:
                    speak("Sorry, I couldn't understand that.")
                except sr.RequestError as e:
                    speak("Speech service is currently unavailable.")
                    logger.error("Speech recognition request error: %s", e)
    except KeyboardInterrupt:
        speak("Shutting down. Goodbye!")
        logger.info("User requested shutdown")


if __name__ == "__main__":
    main_loop()