from tkinter import *
from tkinter import ttk
import time

# =========================
# Configuration Constants
# =========================

# Game Settings
WIN_POINTS = 11          # Points required to win a game
WIN_DIFFERENCE = 2       # Minimum point difference to win
SWAP_SERVE_EVERY = 5
SWAP_SERVE_AFTER = SWAP_SERVE_EVERY - 1  # After how many points to swap serve

# Button Interaction Settings
CLICK_THRESHOLD = 0.3          # Seconds for double-click detection
RESET_HOLD_THRESHOLD = 3       # Seconds to hold button to reset

# Color Schemes
BG_COLOR = "#2C3E50"               # Background color of the main window
MAIN_FRAME_BG = "#34495E"          # Background color of the main frame
PLAYER_FRAME_BG = "#2C3E50"        # Background color of each player's frame
PLAYER_LABEL_COLOR = "white"       # Text color for player labels
SCORE_LABEL_COLOR = "white"        # Text color for score labels
SERVING_COLOR = "#E74C3C"          # Color indicating which player is serving

# Font Settings
PLAYER_LABEL_FONT = ("Arial", 36, "bold")
SCORE_LABEL_FONT = ("Arial", 100, "bold")
GAMES_WON_FONT = ("Arial", 24)
WIN_MESSAGE_FONT = ("Arial", 48, "bold")

# GPIO Button Pins (for Raspberry Pi)
PLAYER1_BUTTON_PIN = 26
PLAYER2_BUTTON_PIN = 18

# =========================
# Ping Pong Scoreboard Class
# =========================

# Try to import GPIO for Raspberry Pi
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

        # Remove window decorations (borders, title bar) for GPIO usage
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
        self.player1_games_won = 0
        self.player2_games_won = 0

        # Initialize button states and press timing
        self.button_pressed = {1: False, 2: False}
        self.button_press_start_time = {1: None, 2: None}

        # Initialize reset flags
        self.reset_occurred = {1: False, 2: False}

        # Initialize click timers for double-click detection
        self.click_timer = {1: None, 2: None}

        # Create a label for displaying win messages
        self.win_message_label = ttk.Label(
            master, 
            text="", 
            font=WIN_MESSAGE_FONT, 
            style='Score.TLabel'
        )
        self.win_message_label.pack(pady=20)

        self.create_widgets()
        self.update_display()

        # Start checking button inputs
        if USE_GPIO:
            self.check_buttons()

        # Optional: Bind the Esc key to exit the application
        master.bind("<Escape>", lambda e: self.exit_app())

    def create_widgets(self):
        # Create the scoreboard layout
        self.main_frame = ttk.Frame(
            self.master, 
            padding=20, 
            style='Main.TFrame'
        )
        self.main_frame.pack(expand=True, fill=BOTH)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=3)

        # Player 1 Frame
        self.player1_frame = ttk.Frame(
            self.main_frame, 
            padding=10, 
            style='Player.TFrame'
        )
        self.player1_frame.grid(row=1, column=0, sticky="nsew")
        self.player1_label = ttk.Label(
            self.player1_frame, 
            text="Player 1", 
            font=PLAYER_LABEL_FONT, 
            style='Player.TLabel'
        )
        self.player1_label.pack(pady=(0, 10))
        self.player1_score_label = ttk.Label(
            self.player1_frame, 
            text="0", 
            font=SCORE_LABEL_FONT, 
            style='Score.TLabel'
        )
        self.player1_score_label.pack()
        self.player1_games_label = ttk.Label(
            self.player1_frame, 
            text="Games Won: 0", 
            font=GAMES_WON_FONT, 
            style='Player.TLabel'
        )
        self.player1_games_label.pack()

        # Player 2 Frame
        self.player2_frame = ttk.Frame(
            self.main_frame, 
            padding=10, 
            style='Player.TFrame'
        )
        self.player2_frame.grid(row=1, column=1, sticky="nsew")
        self.player2_label = ttk.Label(
            self.player2_frame, 
            text="Player 2", 
            font=PLAYER_LABEL_FONT, 
            style='Player.TLabel'
        )
        self.player2_label.pack(pady=(0, 10))
        self.player2_score_label = ttk.Label(
            self.player2_frame, 
            text="0", 
            font=SCORE_LABEL_FONT, 
            style='Score.TLabel'
        )
        self.player2_score_label.pack()
        self.player2_games_label = ttk.Label(
            self.player2_frame, 
            text="Games Won: 0", 
            font=GAMES_WON_FONT, 
            style='Player.TLabel'
        )
        self.player2_games_label.pack()

        # Add style
        style = ttk.Style()
        style.configure('Main.TFrame', background=MAIN_FRAME_BG)
        style.configure('Player.TFrame', background=PLAYER_FRAME_BG)
        style.configure('Player.TLabel', background=PLAYER_FRAME_BG, foreground=PLAYER_LABEL_COLOR)
        style.configure('Score.TLabel', background=PLAYER_FRAME_BG, foreground=SCORE_LABEL_COLOR)
        style.configure('TButton', font=("Arial", 16), padding=10)

    def update_display(self):
        # Update scores and display
        self.player1_score_label.config(text=str(self.player1_score))
        self.player2_score_label.config(text=str(self.player2_score))
        self.player1_games_label.config(text=f"Games Won: {self.player1_games_won}")
        self.player2_games_label.config(text=f"Games Won: {self.player2_games_won}")

        # Reset colors and serving labels
        self.player1_score_label.config(foreground=SCORE_LABEL_COLOR)
        self.player2_score_label.config(foreground=SCORE_LABEL_COLOR)

        if self.serving == 1:
            self.player1_score_label.config(foreground=SERVING_COLOR)  # Serving player color
        else:
            self.player2_score_label.config(foreground=SERVING_COLOR)  # Serving player color

    def add_point(self, player):
        if self.player1_score >= SWAP_SERVE_AFTER or self.player2_score >= SWAP_SERVE_AFTER:
            # Swap serve every point if score is SWAP_SERVE_AFTER or more
            self.serving = 2 if self.serving == 1 else 1

        if player == 1:
            self.player1_score += 1
        else:
            self.player2_score += 1

        # Check for game win condition
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
        # Display the win message
        self.win_message_label.config(text=message)
        self.master.after(2000, self.reset_scores)  # Delay reset for 2 seconds

    def reset_scores(self):
        # Reset scores and games won for a new game
        self.player1_score = 0
        self.player2_score = 0
        self.player1_games_won = 0
        self.player2_games_won = 0
        self.win_message_label.config(text="")  # Clear win message
        self.update_display()

    def schedule_single_click(self, player):
        """Schedule the single click action after CLICK_THRESHOLD seconds."""
        self.click_timer[player] = self.master.after(
            int(CLICK_THRESHOLD * 1000), 
            lambda: self.handle_single_click(player)
        )

    def cancel_single_click(self, player):
        """Cancel the scheduled single click action."""
        if self.click_timer[player] is not None:
            self.master.after_cancel(self.click_timer[player])
            self.click_timer[player] = None

    def handle_single_click(self, player):
        """Handle a single click by adding a point."""
        self.add_point(player)
        self.click_timer[player] = None

    def toggle_serving(self):
        """Toggle the serving player between Player 1 and Player 2."""
        self.serving = 2 if self.serving == 1 else 1
        self.update_display()

    def check_buttons(self):
        # GPIO logic to check button states
        for player, pin in [(1, PLAYER1_BUTTON_PIN), (2, PLAYER2_BUTTON_PIN)]:
            if GPIO.input(pin) == GPIO.LOW:  # Button pressed
                if not self.button_pressed[player]:  # If not already pressed
                    self.button_pressed[player] = True
                    self.button_press_start_time[player] = time.time()  # Record start time
                else:  # If button is already pressed
                    # Check if the button has been held long enough to reset
                    elapsed_time = time.time() - self.button_press_start_time[player]
                    if elapsed_time >= RESET_HOLD_THRESHOLD:
                        self.reset_scores()  # Reset the scores and games won
                        self.button_pressed[player] = False  # Prevent repeated resets
                        self.reset_occurred[player] = True  # Set reset flag
                        # When a reset occurs, do not handle click actions
                        self.cancel_single_click(player)  # Cancel any pending single click
                        continue  # Skip point addition
            else:  # Button released
                if self.button_pressed[player]:  # If it was pressed
                    self.button_pressed[player] = False
                    self.button_press_start_time[player] = None  # Reset start time
                    if not self.reset_occurred[player]:
                        if self.click_timer[player] is not None:
                            # Second click detected within threshold, double-click
                            self.cancel_single_click(player)
                            self.toggle_serving()  # Toggle serving regardless of which button was double-clicked
                        else:
                            # Start a single-click timer
                            self.schedule_single_click(player)
                    else:
                        # Reset occurred, do not add a point
                        self.reset_occurred[player] = False  # Reset the flag
                else:
                    continue  # If it wasn't pressed, do nothing

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