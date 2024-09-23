import RPi.GPIO as GPIO
import time

# GPIO Setup
GPIO.setmode(GPIO.BCM)
PLAYER1_BUTTON = 26
PLAYER2_BUTTON = 18
GPIO.setup(PLAYER1_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PLAYER2_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_test():
    last_press_time = {1: 0, 2: 0}

    try:
        while True:
            for player, pin in [(1, PLAYER1_BUTTON), (2, PLAYER2_BUTTON)]:
                if GPIO.input(pin) == GPIO.LOW:  # Button press detected
                    current_time = time.time()
                    time_since_last = current_time - last_press_time[player]

                    if time_since_last > 0.5:  # Debounce threshold of 0.5 seconds
                        print(f"Player {player} button pressed")
                    last_press_time[player] = current_time

            time.sleep(0.1)  # Check every 100ms

    except KeyboardInterrupt:
        # Cleanup GPIO when the program is interrupted
        GPIO.cleanup()
        print("\nProgram exited cleanly")

if __name__ == "__main__":
    button_test()
