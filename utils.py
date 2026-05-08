# Shared utilities to be imported/used across all files
# Created By: Shreeneel Tarale
# Created Date: 13/04/2026 
# Version: v0.1


import time
from pymata4 import pymata4

import config
from config import *


def read_integer(prompt, min=None, max=None):
    """
    function read_integer
    Validates user input until an integer is obtained, given a prompt to acquire the integer.

    Takes:
        prompt - the message to print to gain an input (string)
        min (optional) - an optional minimum (int)
        max (optional) - an optional maximum (int)

    Returns:
        userInput - the users inputted integer (int)

    """
    while True:
        try: 
            userInput = int(str(input(prompt)))
            if isinstance(userInput, int):
                if (min==None and max==None):
                    return userInput
                elif (min <= userInput <= max):
                    return userInput
                else:
                    print(f"The value you entered must be between {min} and {max}.")
        except ValueError:
            print("The value you entered is invalid. Please enter an integer.")


def read_float(prompt, min=None, max=None):
    """
    function read_float
    Validates user input until a float is obtained, given a prompt to acquire the float.

    Takes:
        prompt - the message to print to gain an input (string)
        min (optional) - an optional minimum (float)
        max (optional) - an optional maximum (float)

    Returns:
        userInput - the users inputted float (float)

    """
    while True:
        try: 
            userInput = float(str(input(prompt)))
            if isinstance(userInput, float):
                if (min==None and max==None):
                    return userInput
                elif (min <= userInput <= max):
                    return userInput
                else:
                    print(f"The value you entered must be between {min} and {max}.")
        except ValueError:
            print("The value you entered is invalid. Please enter a numerical value.")


        

def poll(pin, sonar=False):

    original = time.time()


    while True:
        present = time.time()
        if (present - original)<=pollingRate:
            time.sleep(0.005)
        elif (present - original)>pollingRate:
            return board.digital_read(pin) if not sonar else board.sonar_read(pin)


def poll_us(pin, usNumber):

    

    #calculate rolling avg.
    samples = []
    for i in range(5):
        raw = poll(pin, sonar=True)[0]
        samples.append(raw)
        time.sleep(0.01)
    
    avg_raw = sum(samples)/len(samples)
    height = (sensorMountHeight*100 - avg_raw)/100
    result = height > overheightLimit

    if result:
        state[f"us{usNumber}"]["detected"] = True 
        state[f"us{usNumber}"]["timeOfLast"] = time.time()
        
    else:
        state[f"us{usNumber}"]["detected"] = False

    return result, height, time.strftime("%X %x")

