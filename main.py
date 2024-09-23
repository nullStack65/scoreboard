from tkinter import *
from tkinter import ttk
import time

# Try to import GPIO for Raspberry Pi
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    PLAYER1_BUTTON = 26
    PLAYER2_BUTTON = 18
    GPIO.setup(PLAYER1_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PLAYER2_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    USE_GPIO = True
except ImportError:
    USE_GPIO = False

# For keyboard input when not on RPI
if not USE_GPIO:
    from pynput import keyboard

class PingPongScoreboard:
    def __init__(self, master):
        self.master = master
        master.title("Ping Pong Scoreboard")

        # Remove window decorations (borders, title bar)
        if USE_GPIO:
            master.overrideredirect(True)
            master.update_idletasks()  # Ensure screen size is updated
            screen_width = master.winfo_screenwidth()
            screen_height = master.winfo_screenheight()
            master.geometry(f"{screen_width}x{screen_height}+0+0")
            master.resizable(False, False)
            master.attributes('-topmost', True)
        else:
            master.geometry("1024x600")

        # Initialize scores and serving
        self.player1_score = 0
        self.player2_score = 0
        self.serving = 1  # Player 1 starts serving

        # Initialize button states and press times
        self.button_pressed = {1: False, 2: False}
        self.button_pressed_time = {1: 0, 2: 0}

        # Initialize double-click detection
        self.last_click_time = 0
        self.click_threshold = 0.3  # seconds for double-click detection

        self.create_widgets()
        self.update_display()

        # Start checking button inputs
        if USE_GPIO:
            self.check_buttons()
        else:
            self.setup_keyboard_controls()

        # Optional: Bind the Esc key to exit the application
        master.bind("<Escape>", lambda e: self.exit_app())
        master.bind("<Double-Button-1>", self.handle_double_click)  # Bind double click

    def create_widgets(self):
        # Create the scoreboard layout
        self.main_frame = ttk.Frame(self.master, padding=20)
        self.main_frame.pack(expand=True, fill=BOTH)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=3)
        self.main_frame.rowconfigure(2, weight=1)

        # Player 1 Frame
        self.player1_frame = ttk.Frame(self.main_frame, padding=10)
        self.player1_frame.grid(row=1, column=0, sticky="nsew")
        self.player1_label = ttk.Label(self.player1_frame, text="Player 1", font=("Arial", 36))
        self.player1_label.pack(pady=(0, 10))
        self.player1_score_label = ttk.Label(self.player1_frame, text="0", font=("Arial", 100))
        self.player1_score_label.pack()

        # Player 2 Frame
        self.player2_frame = ttk.Frame(self.main_frame, padding=10)
        self.player2_frame.grid(row=1, column=1, sticky="nsew")
        self.player2_label = ttk.Label(self.player2_frame, text="Player 2", font=("Arial", 36))
        self.player2_label.pack(pady=(0, 10))
        self.player2_score_label = ttk.Label(self.player2_frame, text="0", font=("Arial", 100))
        self.player2_score_label.pack()

    def update_display(self):
        # Update scores and display
        self.player1_score_label.config(text=str(self.player1_score))
        self.player2_score_label.config(text=str(self.player2_score))

        # Reset colors and serving labels
        self.player1_score_label.config(foreground="black")
        self.player2_score_label.config(foreground="black")

        if self.serving == 1:
            self.player1_score_label.config(foreground="red")
        else:
            self.player2_score_label.config(foreground="red")

    def add_point(self, player):
        if player == 1:
            self.player1_score += 1
        else:
            self.player2_score += 1
        self.update_display()

    def check_buttons(self):
        # GPIO logic to check button states
        current_time = time.time()
        for player, pin in [(1, PLAYER1_BUTTON), (2, PLAYER2_BUTTON)]:
            if GPIO.input(pin) == GPIO.LOW:
                # Button handling logic here...
                pass  # (similar to your existing logic)

        self.master.after(50, self.check_buttons)

    def setup_keyboard_controls(self):
        # Setup keyboard controls using pynput
        def on_press(key):
            try:
                if key.char == 'a':  # Simulate Player 1 button
                    self.add_point(1)
                elif key.char == 'l':  # Simulate Player 2 button
                    self.add_point(2)
            except AttributeError:
                pass  # Handle special keys if needed

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def handle_double_click(self, event):
        current_time = time.time()
        if current_time - self.last_click_time <= self.click_threshold:
            # Double click detected
            self.change_server()
        self.last_click_time = current_time

    def change_server(self):
        # Change the serving player
        self.serving = 1 if self.serving == 2 else 2
        self.update_display()

    def exit_app(self):
        if USE_GPIO:
            GPIO.cleanup()
        self.master.destroy()

if __name__ == "__main__":
    root = Tk()
    app = PingPongScoreboard(root)
    root.mainloop()
