import tkinter as tk
from tkinter import Toplevel
import cv2
import numpy as np
import mss
from threading import Thread
import pyautogui
import time

def move_mouse(x, y, duration=1):
    """
    Moves the mouse to a specific position on the screen.
    :param x: X-coordinate on the screen.
    :param y: Y-coordinate on the screen.
    :param duration: Time taken to move the mouse.
    """
    pyautogui.moveTo(x, y, duration=duration)
    print(f"Mouse moved to ({x}, {y})")

def simulate_spacebar():
    """
    Simulates a spacebar press.
    """
    pyautogui.press('space')
    print("Spacebar pressed")

def start_live_view():
    """Function to start the live screen capture in a new window."""
    # Create a new top-level window
    live_window = Toplevel(root)
    live_window.title("Live Screen Capture")

    # Define the screen capture region
    capture_region = {"top": 132, "left": 970, "width": 614, "height": 180}

    # Create a label in the new window to show the video feed
    video_label = tk.Label(live_window)
    video_label.pack()

    # Function to capture the screen and display it
    def capture_screen():
        with mss.mss() as sct:
            while True:
                screenshot = sct.grab(capture_region)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Convert the frame to an image that Tkinter can display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(frame, (700, 400))
                img = np.array(img, dtype=np.uint8)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                tk_image = tk.PhotoImage(data=cv2.imencode('.png', img)[1].tobytes())
                
                # Update the video label
                video_label.configure(image=tk_image)
                video_label.image = tk_image

                # Break the loop if the window is closed
                if not live_window.winfo_exists():
                    break

    # Run the capture function in a separate thread to avoid blocking the GUI
    Thread(target=capture_screen, daemon=True).start()

# Create the main application window
root = tk.Tk()
root.title("Screen Capture App")
root.geometry("600x400")

# Add a button to start the live screen capture
start_button = tk.Button(root, text="Start Screen Capture", command=start_live_view)
start_button.pack(pady=50)
 
# Wait for 2 seconds
time.sleep(10)

# Move mouse to (100, 100) over 1 second
move_mouse(700, 150)

# Wait for 2 seconds
time.sleep(2)

# Simulate spacebar press
simulate_spacebar()

# Run the Tkinter main loop
root.mainloop()