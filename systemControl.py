import os
import sys
import time

def shutdown_system():
    """Gracefully close all apps and shut down the system."""
    try:
        print("Closing all applications and shutting down...")
        time.sleep(1)
        if sys.platform.startswith("win"):
            os.system("shutdown /s /t 5")
        elif sys.platform.startswith("darwin"):
            os.system("osascript -e 'tell app \"System Events\" to shut down'")
        else:
            os.system("shutdown now")
        return True
    except Exception as e:
        print(f"Error shutting down: {e}")
        return False


def restart_system():
    """Restart the system."""
    try:
        print("Restarting the system...")
        time.sleep(1)
        if sys.platform.startswith("win"):
            os.system("shutdown /r /t 5")
        elif sys.platform.startswith("darwin"):
            os.system("osascript -e 'tell app \"System Events\" to restart'")
        else:
            os.system("reboot")
        return True
    except Exception as e:
        print(f"Error restarting: {e}")
        return False
    
def sleep_system():
    """Put the system to sleep."""
    try:
        print("Putting the system to sleep...")
        time.sleep(1)
        if sys.platform.startswith("win"):
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif sys.platform.startswith("darwin"):
            os.system("pmset sleepnow")
        else:
            os.system("systemctl suspend")
        return True
    except Exception as e:
        print(f"Error putting system to sleep: {e}")
        return False
    
def lock_system():
    """Lock the system."""
    try:
        print("Locking the system...")
        time.sleep(1)
        if sys.platform.startswith("win"):
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif sys.platform.startswith("darwin"):
            os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")
        else:
            os.system("gnome-screensaver-command -l")
        return True
    except Exception as e:
        print(f"Error locking system: {e}")
        return False