# this is the windows key listener for the keyboard teleop package (run on windows only)
from pynput import keyboard
import socket


def send_key(msg):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 5555))
            s.sendall(msg.encode())
    except:
        pass  # Handle connection errors gracefully


def on_press(key):
    send_key(f"DOWN:{key}")


def on_release(key):
    send_key(f"UP:{key}")
    if key == keyboard.Key.esc:
        # Stop listener
        return False


with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
