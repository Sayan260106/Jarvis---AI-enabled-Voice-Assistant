import os
import time
import webbrowser
import logging
import threading
import sys
import pyautogui
import speech_recognition as sr
import pyttsx3
from typing import Optional
import pygetwindow as gw
import appManager
import nativeAppManager
import systemControl
import appCloser
import windowManager

# Use Smart YouTube Media Controller (Selenium version)
import mediaControl as mediaControl

try:
    from clint import ask_ai, AIClientError
    import musicLibrary
except Exception:
    pass

# --- Logger ---
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("Jarvis")

# --- TTS Engine ---
engine = pyttsx3.init("sapi5" if sys.platform.startswith("win") else None)
voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

def speak(text: str, block: bool = True) -> None:
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

# --- AI Bridge ---
def aiProcess(command: str) -> str:
    try:
        reply = ask_ai(command)
        return reply
    except NameError:
        logger.warning("AI client not available.")
        return "AI client not configured."
    except AIClientError as e:
        logger.error("AI client error: %s", e)
        return f"AI error: {e}"
    except Exception as e:
        logger.exception("Unexpected AI error: %s", e)
        return "Error contacting AI."

# --- Helper: Open URLs ---
def open_url(url: str) -> None:
    logger.info("Opening: %s", url)
    webbrowser.open(url)

# --- Command Processing ---
def processCommand(command: str, driver=None) -> None:
    c = (command or "").strip().lower()
    logger.info("Processing command: %s", c)
    if not c:
        speak("I didn't hear a command.")
        return

    # --- Basic URLs ---
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
    if "open github" in c:
        open_url("https://www.github.com")
        speak("Opening GitHub")
        return

    # --- Play Music Library ---
    if c.startswith("play "):
        song = c[5:].strip()
        link = musicLibrary.get_link(song)
        if link:
            open_url(link)
            speak(f"Playing {song}")
        else:
            available = ", ".join(musicLibrary.list_songs().keys())
            speak(f"I couldn't find {song}. Available songs: {available}")
        return

    # --- Open Apps or Files ---
    if c.startswith("open "):
        target = c.replace("open ", "").strip()
        if appManager.open_item(target) or nativeAppManager.open_system_app(target):
            speak(f"Opening {target}")
        else:
            speak(f"Sorry, I couldn't find {target}.")
        return

    # --- System Commands ---
    if "shutdown" in c or "turn off" in c:
        speak("Shutting down. Goodbye!")
        systemControl.shutdown_system()
        return
    if "restart" in c or "reboot" in c:
        speak("Restarting system.")
        systemControl.restart_system()
        return
    if "sleep" in c or "hibernate" in c:
        speak("Putting system to sleep.")
        systemControl.sleep_system()
        return
    if "lock" in c:
        speak("Locking system.")
        systemControl.lock_system()
        return

    # --- Close Apps / Tabs ---
    if c.startswith("close "):
        target = c.replace("close ", "").strip()
        if target == "tab":
            appCloser.close_tab()
            return
        if target == "window":
            appCloser.close_window()
            return
        if target in ["all", "everything"]:
            appCloser.confirm_close_all()
            return
        if appCloser.close_app(target):
            speak(f"Closed {target}")
        else:
            speak(f"Couldn't close {target}")
        return

    # --- Smart YouTube / Media Control ---
    if ("pause" in c or "play" in c) and driver:
        mediaControl.play_pause(driver)
        return
    if ("next" in c or "skip" in c) and driver:
        mediaControl.next_video(driver)
        return
    if ("mute" in c or "unmute" in c) and driver:
        mediaControl.mute_unmute(driver)
        return
    if ("volume up" in c or "increase volume" in c or "louder" in c) and driver:
        mediaControl.volume_up(driver)
        return
    if ("volume down" in c or "decrease volume" in c or "lower" in c or "quieter" in c) and driver:
        mediaControl.volume_down(driver)
        return

    # --- Window Control ---
    if "maximize" in c:
        app_name = c.replace("maximize", "").strip()
        if app_name:
            speak(f"Maximizing {app_name}")
            windowManager.maximize_app(app_name)
        else:
            speak("Please specify which app to maximize.")
        return
    if "next tab" in c or "switch tab" in c:
        speak("Switching to next tab")
        windowManager.next_tab()
        return
    if c.startswith("minimize "):
        target = c.replace("minimize ", "").strip()
        if target == "all":
            speak("Minimizing all windows")
            windowManager.minimize_all_window()
            return
        else:
            speak("Minimizing current window")
            windowManager.minimize_window()
            return

    speak("Sorry, I couldn't process that command.")

# --- Voice Listening Loop ---
def listen_for_wakeword(recognizer: sr.Recognizer, mic: sr.Microphone) -> Optional[str]:
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
        text = recognizer.recognize_google(audio)
        return text
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return None
    except sr.RequestError as e:
        logger.error("Speech recognition API error: %s", e)
        return None

# --- Main Loop ---
import pygetwindow as gw

def main_loop():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    speak("Initializing Jarvis...")

    driver = None
    ad_thread = None
    youtube_connected = False

    try:
        while True:
            time.sleep(0.5)  # small delay to avoid CPU overuse

            # --- Check if YouTube is open in Microsoft Edge ---
            yt_open = any(
                "youtube" in win.title.lower() and "edge" in win.title.lower()
                for win in gw.getWindowsWithTitle("YouTube")
            )

            # --- If YouTube opens and not yet connected, start smart control ---
            if yt_open and not youtube_connected:
                try:
                    speak("Detected YouTube open in Microsoft Edge. Connecting smart controller.")
                    driver = mediaControl.get_youtube_driver("edge")
                    time.sleep(5)
                    ad_thread = threading.Thread(
                        target=mediaControl.auto_skip_ads,
                        args=(driver,),
                        daemon=True
                    )
                    ad_thread.start()
                    speak("Smart YouTube controller active. Ad-skip monitor running.")
                    youtube_connected = True
                except Exception as e:
                    speak("Failed to start YouTube smart control.")
                    print("Error:", e)

            # --- If YouTube closed and controller still active, disconnect ---
            elif not yt_open and youtube_connected:
                speak("YouTube window closed. Disconnecting smart controller.")
                try:
                    if driver:
                        driver.quit()
                    driver = None
                    youtube_connected = False
                    speak("Smart YouTube controller stopped.")
                except Exception as e:
                    print("Error closing driver:", e)

            # --- Wake-word & command listening ---
            time.sleep(0.1)
            logger.debug("Listening for wake word...")
            recognized = listen_for_wakeword(recognizer, mic)
            # recognized = input("Enter wake word: ") # Only for testing
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
                    # command = input("Enter command: ") # Only for testing
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
        logger.info("User requested shutdown.")
        
    finally:
        if driver:
            try:
                driver.quit()
                speak("Closed YouTube browser.")
            except:
                pass

if __name__ == "__main__":
    main_loop()