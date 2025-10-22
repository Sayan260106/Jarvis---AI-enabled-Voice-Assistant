import os
import psutil
import subprocess
import pyttsx3
import speech_recognition as sr
import pyautogui

# --- Common app process names ---
COMMON_APPS = {
    "chrome": "chrome.exe",
    "microsoft": "msedge.exe",
    "firefox": "firefox.exe",
    "brave": "brave.exe",
    "vs code": "Code.exe",
    "notepad": "notepad.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "spotify": "Spotify.exe",
    "discord": "Discord.exe",
}

# --- TTS setup ---
engine = pyttsx3.init("sapi5" if os.name == "nt" else None)
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)


def speak(text):
    """Speak and print text."""
    print(f"Jarvis says: {text}")
    engine.say(text)
    engine.runAndWait()


def listen() -> str:
    """Listen for a short voice response."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            speak("I didn't hear anything.")
            return ""
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand that.")
            return ""
        except sr.RequestError:
            speak("Speech service is currently unavailable.")
            return ""


# --- App Closing ---
def close_app(name: str) -> bool:
    """Close a specific app by name using taskkill or process search."""
    if not name:
        return False

    name = name.lower().strip()
    process_name = COMMON_APPS.get(name, name + ".exe")

    try:
        os.system(f"taskkill /F /IM \"{process_name}\" >nul 2>&1")
        return True
    except Exception as e:
        print(f"Error closing {name}: {e}")
        return False


def close_all():
    """Close all user-launched apps, including browsers."""
    try:
        for proc in psutil.process_iter(attrs=["name"]):
            pname = proc.info["name"]
            if pname and any(ext in pname.lower() for ext in [
                "chrome", "firefox", "brave", "edge", "code",
                "notepad", "word", "excel", "powerpnt", "spotify", "discord"
            ]):
                try:
                    proc.kill()
                except Exception:
                    pass
        return True
    except Exception as e:
        print("Error closing all apps:", e)
        return False


# --- Tab and Window Control ---
def close_tab():
    """Close current tab in a browser or app using Ctrl+W."""
    speak("Closing the current tab.")
    pyautogui.hotkey("ctrl", "w")


def close_window():
    """Close current window using Alt+F4."""
    speak("Closing the current window.")
    pyautogui.hotkey("alt", "f4")


def confirm_close_all() -> bool:
    """Ask for voice confirmation before closing all apps."""
    speak("Are you sure you want to close everything? Please say yes or no.")
    response = listen()

    if "yes" in response:
        speak("Alright, closing everything now.")
        close_all()
        return True
    elif "no" in response:
        speak("Okay, I will not close anything.")
        return False
    else:
        speak("I didn't get a clear answer. Cancelling for safety.")
        return False
