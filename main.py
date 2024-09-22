import RPi.GPIO as GPIO
from tkinter import *
from tkinter import ttk
import time

# GPIO Setup
GPIO.setmode(GPIO.BCM)
PLAYER1_BUTTON = 26
PLAYER2_BUTTON = 18
GPIO.setup(PLAYER1_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PLAYER2_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class PingPongScoreboard:
    def __init__(self, master):
        self.master = master
        master.title("Ping Pong Scoreboard")
        
        # Set window size manually to 1024x600 in landscape mode
        master.geometry("1024x600")
        
        # Optional: Remove window borders and make it fullscreen-like
        # master.overrideredirect(True)
        
        # Make sure the window is on top
        master.attributes('-topmost', True)

        self.player1_score = 0
        self.player2_score = 0
        self.serving = 1  # Player 1 starts serving
        self.last_press_time = {1: 0, 2: 0}

        self.create_widgets()
        self.update_display()

        # Start checking GPIO inputs
        self.check_buttons()

    def create_widgets(self):
        # Use a main frame to hold all widgets with padding
        self.main_frame = ttk.Frame(self.master, padding=20)
        self.main_frame.pack(expand=True, fill=BOTH)

        # Configure grid layout
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=3)
        self.main_frame.rowconfigure(2, weight=1)

        # Player 1 Frame
        self.player1_frame = ttk.Frame(self.main_frame, padding=10)
        self.player1_frame.grid(row=1, column=0, sticky="nsew")
        self.player1_frame.columnconfigure(0, weight=1)
        
        self.player1_label = ttk.Label(self.player1_frame, text="Player 1", font=("Arial", 36))
        self.player1_label.pack(pady=(0, 10))
        
        self.player1_score_label = ttk.Label(self.player1_frame, text="0", font=("Arial", 100))
        self.player1_score_label.pack()
        
        self.player1_serving_label = ttk.Label(self.player1_frame, text="", font=("Arial", 24))
        self.player1_serving_label.pack(pady=(10, 0))

        # Player 2 Frame
        self.player2_frame = ttk.Frame(self.main_frame, padding=10)
        self.player2_frame.grid(row=1, column=1, sticky="nsew")
        self.player2_frame.columnconfigure(0, weight=1)
        
        self.player2_label = ttk.Label(self.player2_frame, text="Player 2", font=("Arial", 36))
        self.player2_label.pack(pady=(0, 10))
        
        self.player2_score_label = ttk.Label(self.player2_frame, text="0", font=("Arial", 100))
        self.player2_score_label.pack()
        
        self.player2_serving_label = ttk.Label(self.player2_frame, text="", font=("Arial", 24))
        self.player2_serving_label.pack(pady=(10, 0))

    def update_display(self):
        # Update scores
        self.player1_score_label.config(text=str(self.player1_score))
        self.player2_score_label.config(text=str(self.player2_score))

        # Reset colors and serving labels
        self.player1_score_label.config(foreground="black")
        self.player2_score_label.config(foreground="black")
        self.player1_serving_label.config(text="")
        self.player2_serving_label.config(text="")

        # Highlight serving player
        if self.serving == 1:
            self.player1_score_label.config(foreground="red")
            self.player1_serving_label.config(text="Serving")
        else:
            self.player2_score_label.config(foreground="red")
            self.player2_serving_label.config(text="Serving")

    def add_point(self, player):
        if player == 1:
            self.player1_score += 1
        else:
            self.player2_score += 1

        self.check_match_point()
        self.update_display()

    def check_match_point(self):
        total_points = self.player1_score + self.player2_score

        if self.player1_score >= 10 or self.player2_score >= 10:
            self.serving = 2 if self.player1_score > self.player2_score else 1
        else:
            if total_points % 5 == 0:
                self.serving = 2 if self.serving == 1 else 1

        if self.player1_score >= 11 and self.player1_score >= self.player2_score + 2:
            self.end_game(1)
        elif self.player2_score >= 11 and self.player2_score >= self.player1_score + 2:
            self.end_game(2)

    def end_game(self, winner):
        # Display winner message across the screen
        winner_message = f"Player {winner} Wins!"
        self.clear_widgets()
        winner_label = ttk.Label(self.master, text=winner_message, font=("Arial", 72), foreground="green")
        winner_label.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.master.after(3000, self.reset_scores)

    def clear_widgets(self):
        # Clear only the main_frame to prevent unintended widget duplication
        for widget in self.master.winfo_children():
            if widget != self.main_frame:
                widget.destroy()

    def reset_scores(self):
        # Reset scores and serving
        self.player1_score = 0
        self.player2_score = 0
        self.serving = 1
        self.update_display()
        # Remove winner label if it exists
        for widget in self.master.winfo_children():
            if isinstance(widget, ttk.Label) and "Wins!" in widget.cget("text"):
                widget.destroy()

    def check_buttons(self):
        for player, pin in [(1, PLAYER1_BUTTON), (2, PLAYER2_BUTTON)]:
            if GPIO.input(pin) == GPIO.LOW:
                current_time = time.time()
                time_since_last = current_time - self.last_press_time[player]
                
                if time_since_last > 5:
                    print(f"Player {player} button held for reset")
                    self.reset_scores()
                elif time_since_last > 0.5:  # Debounce
                    print(f"Player {player} button pressed for point")
                    self.add_point(player)
                self.last_press_time[player] = current_time
            else:
                print(f"Player {player} button not pressed")

        self.master.after(100, self.check_buttons)  # Check every 100ms

if __name__ == "__main__":
    root = Tk()
    app = PingPongScoreboard(root)
    try:
        root.mainloop()
    finally:
        # Cleanup GPIO on exit
        GPIO.cleanup()
