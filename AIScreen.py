import tkinter as tk
import cv2
import numpy as np
import mss
from threading import Thread
import pyautogui
import time
import os
from pynput import mouse

# Create directories for saving images
os.makedirs("Jump", exist_ok=True)
os.makedirs("Idle", exist_ok=True)

# Global variables
jump_count = 0
idle_count = 0
capture_idle = True  # Used to toggle idle capturing
tk_image = None      # Placeholder for the current Tkinter image
top_left = None      # Top-left coordinate (x, y)
bottom_right = None  # Bottom-right coordinate (x, y)
setting_top_left = False
setting_bottom_right = False


def save_image(image, folder, count):
    """Saves an image to a specific folder with an incrementing filename."""
    filename = os.path.join(folder, f"{count}.png")
    cv2.imwrite(filename, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    print(f"Image saved: {filename}")


def start_live_view():
    """Function to start the live screen capture in a new window."""
    global tk_image, jump_count, idle_count, capture_idle, top_left, bottom_right

    if not top_left or not bottom_right:
        print("Please set both the top-left and bottom-right positions before starting capture.")
        return

    # Define the capture region based on the top-left and bottom-right coordinates
    capture_region = {
        "top": top_left[1],
        "left": top_left[0],
        "width": bottom_right[0] - top_left[0],
        "height": bottom_right[1] - top_left[1],
    }

    # Create a new top-level window
    live_window = tk.Toplevel(root)
    live_window.title("Live Screen Capture")

    # Create a label in the new window to show the video feed
    video_label = tk.Label(live_window)
    video_label.pack()

    # Function to capture the screen and display it
    def capture_screen():
        global tk_image, jump_count, idle_count, capture_idle

        with mss.mss() as sct:
            while True:
                screenshot = sct.grab(capture_region)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                # Convert the frame to an image that Tkinter can display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(frame, (700, 400))
                tk_image = img  # Update the global tk_image

                # Convert to Tkinter-compatible format
                tk_image_tk = tk.PhotoImage(data=cv2.imencode('.png', img)[1].tobytes())

                # Update the video label
                video_label.configure(image=tk_image_tk)
                video_label.image = tk_image_tk

                # Save idle images every 0.5 seconds
                if capture_idle:
                    idle_count += 1
                    save_image(tk_image, "Idle", idle_count)
                    time.sleep(0.5)

                # Break the loop if the window is closed
                if not live_window.winfo_exists():
                    break

    # Run the capture function in a separate thread to avoid blocking the GUI
    Thread(target=capture_screen, daemon=True).start()


# Spacebar key binding to save the current image in the "Jump" folder
def on_spacebar_press(event):
    global tk_image, jump_count
    if tk_image is not None:
        jump_count += 1
        save_image(tk_image, "Jump", jump_count)


def set_position_top_left():
    """Enable setting the top-left position by clicking anywhere on the screen."""
    global setting_top_left
    setting_top_left = True
    print("Click to set the top-left position.")


def set_position_bottom_right():
    """Enable setting the bottom-right position by clicking anywhere on the screen."""
    global setting_bottom_right
    setting_bottom_right = True
    print("Click to set the bottom-right position.")


# Listener for mouse click events
def on_click(x, y, button, pressed):
    global top_left, bottom_right, setting_top_left, setting_bottom_right

    if pressed:  # Only handle mouse press
        if setting_top_left:
            top_left = (x, y)
            setting_top_left = False
            print(f"Top-left position set to: {top_left}")
        elif setting_bottom_right:
            bottom_right = (x, y)
            setting_bottom_right = False
            print(f"Bottom-right position set to: {bottom_right}")


# Start the mouse listener in a separate thread
mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()


# Create the main application window
root = tk.Tk()
root.title("Screen Capture App")
root.geometry("600x400")

# Bind the spacebar key press to save images
root.bind("<space>", on_spacebar_press)

# Add buttons to set top-left and bottom-right positions
set_top_left_button = tk.Button(root, text="Set Top-Left Position", command=set_position_top_left)
set_top_left_button.pack(pady=10)

set_bottom_right_button = tk.Button(root, text="Set Bottom-Right Position", command=set_position_bottom_right)
set_bottom_right_button.pack(pady=10)

# Add a button to start the live screen capture
start_button = tk.Button(root, text="Start Screen Capture", command=start_live_view)
start_button.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
