# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = None
eeprom = ES2EEPROMUtils.ES2EEPROM()

name ='Kud'
number_of_gueses =3
# Print the game banner
def welcome():
    os.system('clear')
    print(" _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")
#    save_scores()
    print(fetch_scores())

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
    i = 0
    while count > i and i < 3 :
        print("{} - {} took {} guesses".format(i+1,chr(raw_data[i][2]),raw_data[i][3]))
        i = i+1
    pass


# Setup Pins
def setup():
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    GPIO.setup(11,GPIO.OUT)
    GPIO.setup(13,GPIO.OUT)
    GPIO.setup(15,GPIO.OUT)
    GPIO.setup(16,GPIO.IN)
    GPIO.setup(18,GPIO.IN)
    GPIO.setup(32,GPIO.OUT)
    GPIO.setup(33,GPIO.OUT)
    # Setup PWM channels
    pwm_led=GPIO.PWM(32,1000)
    pwm_buzzer=GPIO.PWM(33,1000)
    pwm_led.start(50)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(16, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=200)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=200)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_byte(0)
    scores=[]
    for i in range(3):
        scores.append(eeprom.read_block(i+1,4))
    # convert the codes back to ascii
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    score_count,scores = fetch_scores()
    # include new score
    new_score=[]
    for letter in name:
        new_score.append(ord(letter))
    new_score.append(number_of_gueses) 
    scores.append(new_score)
    # sort
    sorted_scores=sorted(scores, key=lambda x: x[3], reverse = False)
    # update total amount of scores
    eeprom.write_byte(0, score_count+1)
    # write new score
    for i in range(3):
        eeprom.write_block(i+1, sorted_scores[i])
    pass

# Generate guess number 
def generate_number():
     return random.randint(0, pow(2, 3)-1)

# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    state =str( GPIO.input(11))+str(GPIO.input(13))+str(GPIO.input(15))
    new_state=bin(int(state, 2) + int(1, 2))
    for i in 3:
        GPIO.output(LED_value[i], str(new_state)[i])  
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    number_of_gueses = number_of_gueses+1
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    name = input("Enter your name: ")
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    save_scores()
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    pass


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
