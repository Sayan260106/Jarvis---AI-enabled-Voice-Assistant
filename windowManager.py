import pygetwindow as gw
import pyautogui
import time

def maximize_app(app_name):
    try:
        # Find all windows matching the app name
        windows = gw.getWindowsWithTitle(app_name)

        if not windows:
            print(f"No window found for {app_name}")
            return
        
        # Pick the first matching window
        window = windows[0]

        # Bring it to front
        window.activate()
        time.sleep(0.3)  # small delay

        # Maximize it
        if not window.isMaximized:
            window.maximize()

        print(f"{app_name} maximized successfully!")
    except Exception as e:
        print(f"Error maximizing {app_name}: {e}")

# def restore_window():
#     try:
#         # Get the currently active window
#         window = gw.getActiveWindow()
#         if window:
#             window.minimize()
#             print("Window restored successfully!")
#         else:
#             print("No active window found.")
#     except Exception as e:
#         print(f"Error restoring window: {e}")
        
def minimize_window():
    print("Minimizing the current window.")
    pyautogui.hotkey("win", "down")
    time.sleep(0.3)
    pyautogui.hotkey("win", "down")
        
def next_tab():
    """Switch to the next tab in a browser or app using Ctrl+Tab."""
    print("Switching to the next tab.")
    pyautogui.hotkey("ctrl", "tab")
    
def minimize_all_window():
    print("Minimizing all windows.")
    pyautogui.hotkey("win", "m")