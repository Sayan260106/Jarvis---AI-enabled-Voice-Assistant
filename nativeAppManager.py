import os
import subprocess
import sys

# Mapping for common Windows system apps
SYSTEM_APPS = {
    "calculator": "calc.exe",
    "camera": "microsoft.windows.camera:",
    "paint": "mspaint.exe",
    "settings": "ms-settings:",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "wordpad": "write.exe",
    "control panel": "control",
    "notepad": "notepad.exe"
}

def open_system_app(name: str) -> bool:
    """Open a preinstalled Windows app by its friendly name."""
    if not name:
        return False

    key = name.strip().lower()
    target = SYSTEM_APPS.get(key)
    if not target:
        return False

    try:
        if sys.platform.startswith("win"):
            if target.endswith(":"):  # For URI-based apps like camera or settings
                os.system(f"start {target}")
            else:
                subprocess.Popen(target)
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", "-a", key])
        else:
            subprocess.Popen(["xdg-open", key])
        return True
    except Exception as e:
        print(f"Error opening {key}: {e}")
        return False
