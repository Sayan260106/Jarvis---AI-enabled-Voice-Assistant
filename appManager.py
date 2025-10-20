import os
import subprocess
import sys

# --- Mapping of apps/files/folders ---
APP_PATHS = {
    "chrome": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "microsoft": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "notepad": "notepad.exe",
    "studio": r"C:\Users\sayan\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk",
    "downloads": r"C:\Users\sayan\Downloads",
    "documents": r"C:\Users\sayan\Documents",
    # "music": r"C:\Users\sayan\Music",
    "pictures": r"C:\Users\sayan\Pictures",
    # "jarvis project": r"D:\Projects\Jarvis",
    "projects": r"D:\Projects",
    "languages": r"D:\Programming Language",
}

def open_item(name: str) -> bool:
    """Try to open an app, file, or folder by its friendly name."""
    if not name:
        return False

    key = name.strip().lower()
    path = APP_PATHS.get(key)

    if not path:
        return False  # not found

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        print(f"Error opening {path}: {e}")
        return False
