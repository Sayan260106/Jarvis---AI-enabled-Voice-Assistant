import pyautogui
import pyttsx3
import time
import sys
import pygetwindow as gw
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

#--------------- This is for Chrome Browser Usage ---------------------
    # from webdriver_manager.chrome import ChromeDriverManager  
    # from selenium.webdriver.chrome.service import Service
#----------------------------------------------------------------------


# --- TTS Setup ---
engine = pyttsx3.init("sapi5" if sys.platform.startswith("win") else None)
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

def speak(text):
    print(f"Jarvis says: {text}")
    engine.say(text)
    engine.runAndWait()


# --- Utility: Get active window title ---
def get_active_window_title():
    try:
        window = gw.getActiveWindow()
        return window.title.lower() if window else ""
    except:
        return ""


# --- Launch YouTube via Selenium ---

# ---------------------------------------This is for Chrome Browser---------------------------------------
# def get_youtube_driver():
#     """Launch Chrome with Selenium, return driver object."""
#     options = webdriver.ChromeOptions()
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--disable-extensions")
#     options.add_experimental_option("detach", True)

#     driver = webdriver.Edge(
#         service=Service(EdgeChromiumDriverManager().install()),
#         options=options
#     )
#     driver.get("https://www.youtube.com/")
#     return driver
#----------------------------------------------------------------------------------------------------------

#------This is for Edge Browser------
def get_youtube_driver(browser="edge"):
    """Launch Microsoft Edge and open YouTube."""
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("detach", True)

    driver = webdriver.Edge(
        service=Service(EdgeChromiumDriverManager().install()),
        options=options
    )
    driver.get("https://www.youtube.com/")
    return driver


# --- Smart Ad Skipper (Background Thread) ---
def skip_ads_if_present(driver):
    """Detect and click YouTube 'Skip Ads' button."""
    try:
        skip_button = driver.find_element(By.CLASS_NAME, "ytp-ad-skip-button")
        if skip_button.is_displayed():
            speak("Ad detected. Skipping now.")
            skip_button.click()
            time.sleep(1)
            return True
    except NoSuchElementException:
        pass
    except WebDriverException:
        pass
    return False


def auto_skip_ads(driver, interval=2):
    """Continuously monitor and skip ads every few seconds."""
    while True:
        try:
            if skip_ads_if_present(driver):
                time.sleep(1.5)  # brief delay after skipping
            else:
                time.sleep(interval)
        except Exception as e:
            print("Auto-skip thread error:", e)
            time.sleep(5)


# --- YouTube Player Controls ---
def is_video_playing(driver):
    try:
        return driver.execute_script(
            "return document.querySelector('video') && !document.querySelector('video').paused;"
        )
    except:
        return False


def play_pause(driver):
    try:
        if is_video_playing(driver):
            speak("Video is playing. Pausing now.")
            driver.execute_script("document.querySelector('video').pause();")
        else:
            speak("Video is paused. Playing now.")
            driver.execute_script("document.querySelector('video').play();")
    except Exception as e:
        speak(f"Error controlling playback: {e}")


def mute_unmute(driver):
    try:
        muted = driver.execute_script("return document.querySelector('video').muted;")
        driver.execute_script(f"document.querySelector('video').muted = {str(not muted).lower()}")
        speak("Toggled mute state.")
    except Exception as e:
        speak(f"Error toggling mute: {e}")


def volume_up(driver):
    try:
        current = driver.execute_script("return document.querySelector('video').volume;")
        driver.execute_script(f"document.querySelector('video').volume = Math.min({current}+0.1, 1.0);")
        speak("Increased volume.")
    except:
        speak("Could not increase volume.")


def volume_down(driver):
    try:
        current = driver.execute_script("return document.querySelector('video').volume;")
        driver.execute_script(f"document.querySelector('video').volume = Math.max({current}-0.1, 0.0);")
        speak("Decreased volume.")
    except:
        speak("Could not decrease volume.")


def next_video(driver):
    try:
        driver.execute_script(
            "let btn=document.querySelector('a.ytp-next-button'); if(btn) btn.click();"
        )
        speak("Playing next video.")
    except:
        speak("Couldn't go to next video.")