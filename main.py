from tkinter import *
from tkinter import ttk
import time
import math

# =========================
# Configuration Constants
# =========================

# Game Settings
WIN_POINTS = 11
WIN_DIFFERENCE = 2

# Button Interaction Settings
CLICK_THRESHOLD = 0.3
RESET_HOLD_THRESHOLD = 3

# Color Scheme
BG_COLOR = "#1A1A2E"
MAIN_FRAME_BG = "#16213E"
PLAYER_FRAME_BG = "#0F3460"
PLAYER_LABEL_COLOR = "#E94560"
SCORE_LABEL_COLOR = "#FFFFFF"
SERVING_COLOR = "#FFD700"

# Font Settings
PLAYER_LABEL_FONT = ("Roboto", 36, "bold")
SCORE_LABEL_FONT = ("Roboto", 120, "bold")
GAMES_WON_FONT = ("Roboto", 24)
WIN_MESSAGE_FONT = ("Roboto", 48, "bold")

# GPIO Button Pins (for Raspberry Pi)
PLAYER1_BUTTON_PIN = 26
PLAYER2_BUTTON_PIN = 18

# Animation Settings
ANIMATION_DURATION = 500  # milliseconds
ANIMATION_STEPS = 20

# =========================
# Ping Pong Scoreboard Class
# =========================

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PLAYER1_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PLAYER2_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    USE_GPIO = True
except ImportError:
    USE_GPIO = False

class PingPongScoreboard:
    def __init__(self, master):
        self.master = master
        master.title("Ping Pong Scoreboard")
        master.configure(bg=BG_COLOR)

        if USE_GPIO:
            master.attributes("-fullscreen", True)
        else:
            master.geometry("1024x600")

        self.player1_score = 0
        self.player2_score = 0
        self.serving = 1
        self.serve_count = 0
        self.player1_games_won = 0
        self.player2_games_won = 0

        self.button_pressed = {1: False, 2: False}
        self.button_press_start_time = {1: None, 2: None}
        self.reset_occurred = {1: False, 2: False}
        self.click_timer = {1: None, 2: None}

        self.create_widgets()
        self.update_display()

        if USE_GPIO:
            self.check_buttons()

        master.bind("<Escape>", lambda e: self.exit_app())

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Main.TFrame', background=MAIN_FRAME_BG)
        style.configure('Player.TFrame', background=PLAYER_FRAME_BG)
        style.configure('Player.TLabel', background=PLAYER_FRAME_BG, foreground=PLAYER_LABEL_COLOR)
        style.configure('Score.TLabel', background=PLAYER_FRAME_BG, foreground=SCORE_LABEL_COLOR)
        style.configure('Games.TLabel', background=PLAYER_FRAME_BG, foreground=PLAYER_LABEL_COLOR)
        style.configure('Win.TLabel', background=MAIN_FRAME_BG, foreground=PLAYER_LABEL_COLOR)

        self.main_frame = ttk.Frame(self.master, padding=20, style='Main.TFrame')
        self.main_frame.pack(expand=True, fill=BOTH)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=3)

        self.win_message_label = ttk.Label(
            self.main_frame, 
            text="", 
            font=WIN_MESSAGE_FONT, 
            style='Win.TLabel'
        )
        self.win_message_label.grid(row=0, column=0, columnspan=2, pady=20)

        self.create_player_frame(1)
        self.create_player_frame(2)

    def create_player_frame(self, player):
        frame = ttk.Frame(self.main_frame, padding=10, style='Player.TFrame')
        frame.grid(row=1, column=player-1, sticky="nsew", padx=10)

        label = ttk.Label(
            frame, 
            text=f"Player {player}", 
            font=PLAYER_LABEL_FONT, 
            style='Player.TLabel'
        )
        label.pack(pady=(0, 10))

        score_label = ttk.Label(
            frame, 
            text="0", 
            font=SCORE_LABEL_FONT, 
            style='Score.TLabel'
        )
        score_label.pack()

        games_label = ttk.Label(
            frame, 
            text="Games Won: 0", 
            font=GAMES_WON_FONT, 
            style='Games.TLabel'
        )
        games_label.pack(pady=(10, 0))

        setattr(self, f'player{player}_frame', frame)
        setattr(self, f'player{player}_label', label)
        setattr(self, f'player{player}_score_label', score_label)
        setattr(self, f'player{player}_games_label', games_label)

    def update_display(self):
        self.animate_score_change(1)
        self.animate_score_change(2)
        self.player1_games_label.config(text=f"Games Won: {self.player1_games_won}")
        self.player2_games_label.config(text=f"Games Won: {self.player2_games_won}")

        self.player1_score_label.config(foreground=SCORE_LABEL_COLOR)
        self.player2_score_label.config(foreground=SCORE_LABEL_COLOR)

        serving_label = getattr(self, f'player{self.serving}_score_label')
        serving_label.config(foreground=SERVING_COLOR)

    def animate_score_change(self, player):
        score = getattr(self, f'player{player}_score')
        score_label = getattr(self, f'player{player}_score_label')
        current_score = int(score_label.cget('text'))

        if current_score != score:
            self.animate_value(score_label, current_score, score)

    def animate_value(self, widget, start, end):
        steps = ANIMATION_STEPS
        step_time = ANIMATION_DURATION / steps
        
        def animate_step(current_step):
            if current_step <= steps:
                t = current_step / steps
                ease_t = math.sin(t * math.pi / 2)
                value = int(start + (end - start) * ease_t)
                widget.config(text=str(value))
                self.master.after(int(step_time), animate_step, current_step + 1)

        animate_step(0)

    def add_point(self, player):
        if player == 1:
            self.player1_score += 1
        else:
            self.player2_score += 1

        self.serve_count += 1

        if self.player1_score >= 10 and self.player2_score >= 10:
            self.serving = 2 if self.serving == 1 else 1
            self.serve_count = 0
        elif self.serve_count == 2:
            self.serving = 2 if self.serving == 1 else 1
            self.serve_count = 0

        if (self.player1_score >= WIN_POINTS and 
            self.player1_score - self.player2_score >= WIN_DIFFERENCE):
            self.player1_games_won += 1
            self.show_win_message("Player 1 Wins!")
        elif (self.player2_score >= WIN_POINTS and 
              self.player2_score - self.player1_score >= WIN_DIFFERENCE):
            self.player2_games_won += 1
            self.show_win_message("Player 2 Wins!")

        self.update_display()

    def show_win_message(self, message):
        self.win_message_label.config(text=message)
        self.master.after(2000, self.reset_game)

    def reset_game(self):
        self.player1_score = 0
        self.player2_score = 0
        self.serving = 1
        self.serve_count = 0
        self.win_message_label.config(text="")
        self.update_display()

    def reset_scoreboard(self):
        self.player1_score = 0
        self.player2_score = 0
        self.player1_games_won = 0
        self.player2_games_won = 0
        self.serving = 1
        self.serve_count = 0
        self.win_message_label.config(text="")
        self.update_display()

    def schedule_single_click(self, player):
        self.click_timer[player] = self.master.after(
            int(CLICK_THRESHOLD * 1000), 
            lambda: self.handle_single_click(player)
        )

    def cancel_single_click(self, player):
        if self.click_timer[player] is not None:
            self.master.after_cancel(self.click_timer[player])
            self.click_timer[player] = None

    def handle_single_click(self, player):
        self.add_point(player)
        self.click_timer[player] = None

    def toggle_serving(self):
        self.serving = 2 if self.serving == 1 else 1
        self.serve_count = 0
        self.update_display()

    def check_buttons(self):
        for player, pin in [(1, PLAYER1_BUTTON_PIN), (2, PLAYER2_BUTTON_PIN)]:
            if GPIO.input(pin) == GPIO.LOW:
                if not self.button_pressed[player]:
                    self.button_pressed[player] = True
                    self.button_press_start_time[player] = time.time()
                else:
                    elapsed_time = time.time() - self.button_press_start_time[player]
                    if elapsed_time >= RESET_HOLD_THRESHOLD:
                        self.reset_scoreboard()
                        self.button_pressed[player] = False
                        self.reset_occurred[player] = True
                        self.cancel_single_click(player)
                        continue
            else:
                if self.button_pressed[player]:
                    self.button_pressed[player] = False
                    self.button_press_start_time[player] = None
                    if not self.reset_occurred[player]:
                        if self.click_timer[player] is not None:
                            self.cancel_single_click(player)
                            self.toggle_serving()
                        else:
                            self.schedule_single_click(player)
                    else:
                        self.reset_occurred[player] = False
                else:
                    continue

        self.master.after(50, self.check_buttons)

    def exit_app(self):
        if USE_GPIO:
            GPIO.cleanup()
        self.master.destroy()

# =========================
# Main Application Entry
# =========================

if __name__ == "__main__":
    root = Tk()
    app = PingPongScoreboard(root)
    root.mainloop()