import RPi.GPIO as GPIO
from tkinter import *
from tkinter import ttk
import time
import sys

# GPIO Setup
GPIO.setmode(GPIO.BCM)
PLAYER1_BUTTON = 26  # Ensure this is correct
PLAYER2_BUTTON = 18
GPIO.setup(PLAYER1_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PLAYER2_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class PingPongScoreboard:
    def __init__(self, master):
        self.master = master
        master.title("Ping Pong Scoreboard")
        
        # Set window to fullscreen
        master.attributes('-fullscreen', True)
        
        # Make sure the window is on top
        master.attributes('-topmost', True)
        
        # Bind the Escape key to exit the application
        master.bind("<Escape>", lambda e: self.exit_application())
        
        # Initialize scores and serving player
        self.player1_score = 0
        self.player2_score = 0
        self.serving = 1  # Player 1 starts serving
        self.last_press_time = {1: 0, 2: 0}
        
        # Create main frame
        self.main_frame = ttk.Frame(self.master, padding=20)
        self.main_frame.pack(expand=True, fill=BOTH)
        
        # Configure grid layout
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=3)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Create player frames
        self.create_player_frames()
        
        # Create winner overlay (hidden by default)
        self.create_winner_overlay()
        
        # Update the display initially
        self.update_display()
        
        # Setup GPIO event detection
        self.setup_gpio_events()
    
    def create_player_frames(self):
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
    
    def create_winner_overlay(self):
        # Create a frame that overlays the main frame
        self.winner_frame = ttk.Frame(self.master, padding=50, style='Winner.TFrame')
        self.winner_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.winner_frame.lower()  # Hide it initially
        
        self.winner_label = ttk.Label(self.winner_frame, text="", font=("Arial", 72), foreground="green")
        self.winner_label.pack()
    
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
            if total_points % 5 == 0 and total_points != 0:
                self.serving = 2 if self.serving == 1 else 1
        
        if self.player1_score >= 11 and self.player1_score >= self.player2_score + 2:
            self.end_game(1)
        elif self.player2_score >= 11 and self.player2_score >= self.player1_score + 2:
            self.end_game(2)
    
    def end_game(self, winner):
        # Display winner message
        self.winner_label.config(text=f"Player {winner} Wins!")
        self.winner_frame.lift()  # Bring to front
        
        # Schedule to reset scores after 3 seconds
        self.master.after(3000, self.reset_scores)
    
    def reset_scores(self):
        # Hide winner message
        self.winner_frame.lower()
        
        # Reset scores and serving player
        self.player1_score = 0
        self.player2_score = 0
        self.serving = 1
        self.update_display()
    
    def setup_gpio_events(self):
        # Setup event detection for Player 1 Button
        GPIO.add_event_detect(PLAYER1_BUTTON, GPIO.FALLING, callback=self.player1_button_pressed, bouncetime=300)
        
        # Setup event detection for Player 2 Button
        GPIO.add_event_detect(PLAYER2_BUTTON, GPIO.FALLING, callback=self.player2_button_pressed, bouncetime=300)
    
    def player1_button_pressed(self, channel):
        self.handle_button_press(1)
    
    def player2_button_pressed(self, channel):
        self.handle_button_press(2)
    
    def handle_button_press(self, player):
        current_time = time.time()
        time_since_last = current_time - self.last_press_time[player]
        
        if time_since_last > 5:
            print(f"Player {player} button held for reset")
            self.reset_scores()
        elif time_since_last > 0.5:  # Debounce
            print(f"Player {player} button pressed for point")
            self.add_point(player)
        
        self.last_press_time[player] = current_time
    
    def exit_application(self):
        self.master.destroy()
    
    def run(self):
        try:
            self.master.mainloop()
        except KeyboardInterrupt:
            self.exit_application()

if __name__ == "__main__":
    root = Tk()
    
    # Optional: Apply styles for better appearance
    style = ttk.Style()
    style.configure('Winner.TFrame', background='white')
    style.configure('Winner.TLabel', foreground='green', background='white')
    
    app = PingPongScoreboard(root)
    app.run()
    
    # Cleanup GPIO on exit
    GPIO.cleanup()
