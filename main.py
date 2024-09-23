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

class PingPongScoreboard:
    def __init__(self, master):
        self.master = master
        master.title("Ping Pong Scoreboard")
        master.configure(bg="#2C3E50")

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
        self.player1_games_won = 0
        self.player2_games_won = 0

        # Serve count tracking
        self.serve_count = 0
        self.serves_per_change = 2  # Number of serves before automatic server swap

        # Initialize button states and press timing
        self.button_pressed = {1: False, 2: False}
        self.button_press_start_time = {1: None, 2: None}
        self.reset_time_threshold = 5  # seconds for button hold to reset

        # Double-click tracking
        self.click_pending = {1: False, 2: False}
        self.click_after_id = {1: None, 2: None}
        self.click_threshold = 0.5  # seconds for double-click detection

        # Victory message label
        self.victory_label = ttk.Label(master, text="", font=("Arial", 48, "bold"), style='Score.TLabel')
        self.victory_label.pack(pady=20)

        self.create_widgets()
        self.update_display()

        # Start checking button inputs
        if USE_GPIO:
            self.check_buttons()

        # Optional: Bind the Esc key to exit the application
        master.bind("<Escape>", lambda e: self.exit_app())

    def create_widgets(self):
        # Create the scoreboard layout
        self.main_frame = ttk.Frame(self.master, padding=20, style='Main.TFrame')
        self.main_frame.pack(expand=True, fill=BOTH)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=3)

        # Player 1 Frame
        self.player1_frame = ttk.Frame(self.main_frame, padding=10, style='Player.TFrame')
        self.player1_frame.grid(row=1, column=0, sticky="nsew")
        self.player1_label = ttk.Label(self.player1_frame, text="Player 1", font=("Arial", 36, "bold"), style='Player.TLabel')
        self.player1_label.pack(pady=(0, 10))
        self.player1_score_label = ttk.Label(self.player1_frame, text="0", font=("Arial", 100, "bold"), style='Score.TLabel')
        self.player1_score_label.pack()
        self.player1_games_label = ttk.Label(self.player1_frame, text="Games Won: 0", font=("Arial", 24), style='Player.TLabel')
        self.player1_games_label.pack()

        # Player 2 Frame
        self.player2_frame = ttk.Frame(self.main_frame, padding=10, style='Player.TFrame')
        self.player2_frame.grid(row=1, column=1, sticky="nsew")
        self.player2_label = ttk.Label(self.player2_frame, text="Player 2", font=("Arial", 36, "bold"), style='Player.TLabel')
        self.player2_label.pack(pady=(0, 10))
        self.player2_score_label = ttk.Label(self.player2_frame, text="0", font=("Arial", 100, "bold"), style='Score.TLabel')
        self.player2_score_label.pack()
        self.player2_games_label = ttk.Label(self.player2_frame, text="Games Won: 0", font=("Arial", 24), style='Player.TLabel')
        self.player2_games_label.pack()

        # Add style
        style = ttk.Style()
        style.configure('Main.TFrame', background='#34495E')
        style.configure('Player.TFrame', background='#2C3E50')
        style.configure('Player.TLabel', background='#2C3E50', foreground='white')
        style.configure('Score.TLabel', background='#2C3E50', foreground='white')
        style.configure('TButton', font=("Arial", 16), padding=10)

    def update_display(self):
        # Update scores and display
        self.player1_score_label.config(text=str(self.player1_score))
        self.player2_score_label.config(text=str(self.player2_score))
        self.player1_games_label.config(text=f"Games Won: {self.player1_games_won}")
        self.player2_games_label.config(text=f"Games Won: {self.player2_games_won}")

        # Reset colors and serving labels
        self.player1_score_label.config(foreground="white")
        self.player2_score_label.config(foreground="white")

        if self.serving == 1:
            self.player1_score_label.config(foreground="#E74C3C")  # Red for Player 1 serving
        else:
            self.player2_score_label.config(foreground="#E74C3C")  # Red for Player 2 serving

    def add_point(self, player):
        if self.player1_score >= 10 or self.player2_score >= 10:
            # Swap serve every point if score is 10 or more
            self.serving = 2 if self.serving == 1 else 1

        if player == 1:
            self.player1_score += 1
        else:
            self.player2_score += 1

        # Increment serve count
        self.serve_count += 1

        # Check if it's time to swap server automatically
        if self.serve_count >= self.serves_per_change:
            self.swap_server()
            self.serve_count = 0

        # Check for game win condition
        if self.player1_score >= 11 and self.player1_score - self.player2_score >= 2:
            self.player1_games_won += 1
            self.show_win_message("Player 1 Wins!")
        elif self.player2_score >= 11 and self.player2_score - self.player1_score >= 2:
            self.player2_games_won += 1
            self.show_win_message("Player 2 Wins!")

        self.update_display()

    def swap_server(self):
        # Swap the serving player
        self.serving = 2 if self.serving == 1 else 1
        self.update_display()

    def show_win_message(self, message):
        # Display the win message
        self.victory_label.config(text=message)
        self.master.after(2000, self.reset_scores)  # Delay reset for 2 seconds

    def reset_scores(self):
        # Reset scores for a new game
        self.player1_score = 0
        self.player2_score = 0
        self.serve_count = 0  # Reset serve count
        self.victory_label.config(text="")  # Clear win message
        self.update_display()

    def handle_single_click(self, player):
        if self.click_pending[player]:
            self.add_point(player)
            self.click_pending[player] = False
            self.click_after_id[player] = None

    def check_buttons(self):
        current_time = time.time()

        # GPIO logic to check button states
        for player, pin in [(1, PLAYER1_BUTTON), (2, PLAYER2_BUTTON)]:
            if GPIO.input(pin) == GPIO.LOW:  # Button pressed
                if not self.button_pressed[player]:  # If not already pressed
                    self.button_pressed[player] = True
                    self.button_press_start_time[player] = current_time  # Record start time
                else:  # If button is already pressed
                    # Check if the button has been held long enough to reset
                    elapsed_time = current_time - self.button_press_start_time[player]
                    if elapsed_time >= self.reset_time_threshold:
                        self.reset_scores()  # Reset the scores
                        self.button_pressed[player] = False  # Prevent repeated resets
                        self.button_press_start_time[player] = None
                        # Cancel any pending single-click actions
                        if self.click_after_id[player]:
                            self.master.after_cancel(self.click_after_id[player])
                            self.click_after_id[player] = None
                            self.click_pending[player] = False
            else:  # Button released
                if self.button_pressed[player]:  # If it was pressed
                    self.button_pressed[player] = False
                    elapsed_time = current_time - self.button_press_start_time[player]
                    self.button_press_start_time[player] = None  # Reset start time

                    if elapsed_time >= self.reset_time_threshold:
                        # Already handled reset above; do nothing
                        continue

                    # Double-click detection
                    if self.click_pending[player]:
                        # Check if the time since last click is within threshold
                        time_since_last_click = current_time - self.last_click_time.get(player, 0)
                        if time_since_last_click <= self.click_threshold:
                            # Double-click detected
                            if self.click_after_id[player]:
                                self.master.after_cancel(self.click_after_id[player])
                            self.swap_server()
                            self.click_pending[player] = False
                            self.click_after_id[player] = None
                        else:
                            # Not a double-click; treat as single-click
                            self.click_pending[player] = True
                            self.last_click_time[player] = current_time
                            self.click_after_id[player] = self.master.after(int(self.click_threshold * 1000),
                                                                             lambda p=player: self.handle_single_click(p))
                    else:
                        # First click; set pending and wait for possible double-click
                        self.click_pending[player] = True
                        self.last_click_time[player] = current_time
                        self.click_after_id[player] = self.master.after(int(self.click_threshold * 1000),
                                                                         lambda p=player: self.handle_single_click(p))
                else:
                    # Button was not pressed; do nothing
                    continue

        self.master.after(50, self.check_buttons)

    def exit_app(self):
        if USE_GPIO:
            GPIO.cleanup()
        self.master.destroy()

if __name__ == "__main__":
    root = Tk()
    app = PingPongScoreboard(root)
    root.mainloop()
