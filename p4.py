# Import libraries
import RPi.GPIO as GPIO
import random
from time import sleep
import ES2EEPROMUtils
import os
import smbus2 as SMBUS

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
gScores = [] # Scores from current game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()

# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():

    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()

    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        play(value)
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    pass

# Testing only
def test():
    eeprom.clear(32)
    eeprom.populate_mock_scores()

    num, results = fetch_scores()
    print(results)

    #save_scores([{"name": "me", "score": 3}])
    exit()

# Gameplay
def play(random_num):
    pass


# Setup Pins
def setup():
    # Setup board mode
    # Setup regular GPIO
    # Setup PWM channels
    # Setup debouncing and callbacks
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(LED_value, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(btn_increase, GPIO.IN)
    GPIO.setup(btn_submit, GPIO.IN)

# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = 0
    scores = []
    # Get the scores
    score_count = eeprom.read_byte(0)
    
    end_flag = False
    temp = ["", 0]
    for i in range(1, score_count+1):
        current = eeprom.read_block((i), 4)
        name = ""
        print(i)
        print(current)

        for j in range(3):
            temp[0] = temp[0] + chr(current[j])
        
        if (current[3] != 0):
            temp[1] = current[3]      
            end_flag = True  
        
        if (end_flag):
            scores.append(temp)
            end_flag = False
            temp = ["", 0]

    # return back the results
    return score_count, scores


# Save high scores
def save_scores(input_scores):
    # fetch scores
    count, scores = fetch_scores()
    # include new score
    # sort
    # update total amount of scores
    count += len(input_scores) 
    # write new scores


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass

# Sound Buzzer
def trigger_buzzer(offset):
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    buzzer_pwm = GPIO.PWM(buzzer, 800)

    if (offset == 1):
        beeps = 4
    elif (offset == 2):
        beeps = 2
    else:
        beeps = 1
    
    wait = ((1 - (0.05)*beeps)/beeps)

    for i in range(beeps):
        print(wait)
        buzzer_pwm.start(50)
        sleep(0.05)
        buzzer_pwm.stop()
        sleep(wait)


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
       #welcome()
        test()
        while True:
            #menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
