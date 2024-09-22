import RPi.GPIO as GPIO
from tkinter import *
from tkinter import ttk
import time

# GPIO Setup
GPIO.setmode(GPIO.BCM)
PLAYER1_BUTTON = 27
PLAYER2_BUTTON = 18
GPIO.setup(PLAYER1_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PLAYER2_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class PingPongScoreboard:
    def __init__(self, master):
        self.master = master
        master.title("Ping Pong Scoreboard")
        
        # Set window size to match screen resolution
        master.geometry("1024x600")
        
        # Remove window decorations
        master.overrideredirect(True)
        
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
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(3, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(2, weight=1)

        self.player1_label = ttk.Label(self.master, text="Player 1", font=("Arial", 36))
        self.player1_label.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.player2_label = ttk.Label(self.master, text="Player 2", font=("Arial", 36))
        self.player2_label.grid(row=1, column=2, padx=20, pady=10, sticky="nsew")

        self.score_label = ttk.Label(self.master, text="0 - 0", font=("Arial", 72))
        self.score_label.grid(row=2, column=0, columnspan=3, pady=20, sticky="nsew")

        self.serving_label = ttk.Label(self.master, text="Serving: Player 1", font=("Arial", 24))
        self.serving_label.grid(row=3, column=0, columnspan=3, pady=10, sticky="nsew")

    def update_display(self):
        self.score_label.config(text=f"{self.player1_score} - {self.player2_score}")
        self.serving_label.config(text=f"Serving: Player {self.serving}")

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
        self.score_label.config(text=f"Player {winner} Wins!")
        self.master.after(3000, self.reset_scores)

    def reset_scores(self):
        self.player1_score = 0
        self.player2_score = 0
        self.serving = 1
        self.update_display()

    def check_buttons(self):
        for player, pin in [(1, PLAYER1_BUTTON), (2, PLAYER2_BUTTON)]:
            if GPIO.input(pin) == GPIO.LOW:
                current_time = time.time()
                if current_time - self.last_press_time[player] > 5:
                    print(f"Player {player} button held for reset")
                    self.reset_scores()
                elif current_time - self.last_press_time[player] > 0.5:  # Debounce
                    print(f"Player {player} button pressed for point")
                    self.add_point(player)
                self.last_press_time[player] = current_time
            else:
                print(f"Player {player} button not pressed")

        self.master.after(100, self.check_buttons)  # Check every 100ms

if __name__ == "__main__":
    root = Tk()
    app = PingPongScoreboard(root)
    root.mainloop()

    # Cleanup GPIO on exit
    GPIO.cleanup()