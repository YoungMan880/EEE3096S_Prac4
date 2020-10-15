# Import libraries
import RPi.GPIO as GPIO
import random
import time
import ES2EEPROMUtils
import os
import smbus2 as SMBUS
import signal

# some global variables that need to change as we run the program
end_of_game = True  # set if the user wins or ends the game
last_pressed = 0 # last time guess wass pressed
gScore = 0 # Scores from current game
guess = 0
random_value = 0
guess_edge_count = 0
accuracy_pwm = None
buzzer_pwm = None

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
    global gScore
    global end_of_game
    global random_value

    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()

    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        end_of_game = False
        gScore = 0
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        random_value = generate_number()
        while not(end_of_game):
            play()
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    for i in range(3):
        print("{0} - {1} took {2} guesses".format((i + 1), raw_data[i][0], raw_data[i][1]))
    pass

# Testing only
def test():
    num, scores = eeprrom.read_block(0,32)
    print(scores)
    eeprom.write_block(1, [2])
    num, scores = eeprrom.read_block(0,32)
    print(scores)
# Gameplay
def play():
    pass


# Setup Pins
def setup():
    # Setup board mode
    # Setup regular GPIO
    # Setup PWM channels
    # Setup debouncing and callbacks
    global buzzer_pwm
    global accuracy_pwm

    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(LED_value, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    accuracy_pwm = GPIO.PWM(LED_accuracy, 1000)
    buzzer_pwm = GPIO.PWM(buzzer, 800)

    GPIO.output(LED_value, 0)

    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_callback, bouncetime=500)
    GPIO.add_event_detect(btn_submit, GPIO.BOTH, callback=btn_submit_callback, bouncetime=150)

def btn_increase_callback(channel):
    global end_of_game
    global gScore

    print("increase pressed")
    if not(end_of_game):
        btn_increase_pressed()

def btn_submit_callback(channel):
    global end_of_game
    global last_pressed
    global guess_edge_count

    guess_edge_count += 1
    milli_sec = int(round(time.time() * 1000))
    print("sumbit pressed")
    print("edge count: {}".format(guess_edge_count))

    if ((milli_sec - last_pressed > 1000) and (milli_sec - last_pressed < 5000) and ((guess_edge_count % 2) == 0)):
        end_of_game = True
    elif (not(end_of_game) and ((guess_edge_count % 2) == 0)):
        btn_guess_pressed()
    else:
        last_pressed = milli_sec

    
    

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
    scores.extend(input_scores)
    # sort
    scores.sort(key=lambda x: x[1])
    # update total amount of scores
    count += len(input_scores) 
    # write new scores
    eeprom.write_byte(0, count)

    offset = 1
    for i in range(0,count):

        temp = [0,0,0,0]
        if (len(scores[i][0]) < 4):
            temp[0] = ord(scores[i][0][0])
            temp[1] = ord(scores[i][0][1])
            temp[2] = ord(scores[i][0][2])
            temp[3] = scores[i][1]

            eeprom.write_block(i + offset, temp)
        else:
            end_flag = False
            j = 0
            while (not(end_flag)):
                temp = [0,0,0,0]

                temp[0] = ord(scores[i][0][j+0])
                temp[1] = ord(scores[i][0][j+1])
                temp[2] = ord(scores[i][0][j+2])

                eeprom.write_block(i + offset, temp)
                offset += 1
                j += 1
            
        

# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed():
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    global guess
    global random_value

    guess += 1
    GPIO.output(LED_value, 0)

    print("gueess: {0} - Value: {1}".format(guess, random_value))

    diff = bin(abs(guess))
    print(diff)
    if (len(diff) < 5):
        diff = "0b" + ("0" * (5 - len(diff))) + diff[2:]

    print(diff)
    if not((len(diff)-2) > 3):
        for i in range(len(diff)-2):
            GPIO.output(LED_value[i], int(diff[i+2]))

# Guess button
def btn_guess_pressed():
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    global random_value
    global guess
    diff = abs(random_value - guess)
    global gScore
    name = "XXX"
    # Change the PWM LED
    accuracy_leds()
    # if it's close enough, adjust the buzzer
    if (diff < 4):
        trigger_buzzer(diff)
    # if it's an exact guess:
    if (diff == 0):
        # - Disable LEDs and Buzzer
        GPIO.output(LED_value, 0)
        guess = 0
        random_value = 100
        # - tell the user and prompt them for a name
        print("correct guess!")
        name = input("What is your name?")
        save_scores([[name, gScore]])
        end_of_game = True


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    global random_value
    global accuracy_pwm
    global guess
    if(guess>random_value):
     accuracy_pwm.start(((8-guess) / (8-random_value))*100)
    else:
     accuracy_pwm.start((guess/random_value)*100)

# Sound Buzzer
def trigger_buzzer(offset):
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global buzzer_pwm

    if (offset == 1):
        beeps = 4
    elif (offset == 2):
        beeps = 2
    else:
        beeps = 1
    
    wait = ((1 - (0.05)*beeps)/beeps)

    for i in range(beeps):
        buzzer_pwm.start(50)
        time.sleep(0.05)
        buzzer_pwm.stop()
        time.sleep(wait)


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
