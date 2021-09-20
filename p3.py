
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
btn_increase = 36
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()

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
# Print the game menu
def menu():
    global end_of_game
    global value
    global num
    global state_dec
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
        num=0
        state_dec = 0
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
        print("{} - {}{}{} took {} guesses".format(i+1,chr(raw_data[i][0]),chr(raw_data[i][1]),chr(raw_data[i][2]),raw_data[i][3]))
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
    
    GPIO.output(11,GPIO.LOW)
    GPIO.output(13,GPIO.LOW)
    GPIO.output(15,GPIO.LOW)
    
    GPIO.setup(btn_submit,GPIO.IN)
    GPIO.setup(btn_increase,GPIO.IN)
    GPIO.setup(32,GPIO.OUT)
    GPIO.setup(33,GPIO.OUT)
    
    # Setup PWM channels
    global pwm_led
    global pwm_buzzer   
    pwm_led=GPIO.PWM(LED_accuracy,1)
    pwm_buzzer=GPIO.PWM(buzzer,1)
    pwm_led.start(0)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed,bouncetime=200)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=200)
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
    i =0
    for letter in name:
        if i <3:
         new_score.append(ord(letter))
         i=i+1
    while i<3:
     new_score.append(ord(" "))
     i=i+1
    new_score.append(num)
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
def btn_increase_pressed(btn_increase):
    # Increase the value shown on the LEDs
    global state_dec
    state =str( GPIO.input(11))+str(GPIO.input(13))+str(GPIO.input(15))
    new_state= int(state,2)+1
    new_state=str( bin(new_state).replace("0b", "000"))[-3:]
    print(new_state)
    for i in range(3):
        GPIO.output(LED_value[i],int(new_state[i]))  
    # You can choose to have a global variable store the user's current guess,
    state_dec =int(new_state,2) 
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(btn_submit):
    global num
    num = num +1
    accuracy_leds()
    trigger_buzzer()
#    GPIO.clean()
#    menu()
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    if state_dec == value:
        # Change the PWM LED
        # if it's close enough, adjust the buzzer
        # if it's an exact guess:
        # - Disable LEDs and Buzzer
        GPIO.cleanup()
        # - tell the user and prompt them for a name
        global name
        name = input("Enter your name: ")
        # - fetch all the scores
        # - add the new score
        # - sort the scores
        # - Store the scores back to the EEPROM, being sure to update the score count
        save_scores()
        welcome()
        menu()
    pass

# LED Brightness
def accuracy_leds():

    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    if state_dec<value:
        duty = state_dec/value *100
    elif state_dec>value:
        duty=((8-state_dec)/(8-value))*100
    else:
        duty = 0
    pwm_led.ChangeDutyCycle(duty)
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # They buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
      
    if abs(value-state_dec) == 3:
        pwm_buzzer.ChangeFrequency(0.5)
        pwm_buzzer.start(50) 
    elif abs(value-state_dec) == 2:
        pwm_buzzer.ChangeFrequency(2)
        pwm_buzzer.start(50)
    elif abs(value-state_dec) == 1:
        pwm_buzzer.ChangeFrequency(4)
        pwm_buzzer.start(50)
    else:
     pwm_buzzer.stop()
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
