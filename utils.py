# utils.py
# Shared utilities to be imported/used across all files
# Created By: Shreeneel Tarale
# Created Date: 13/04/2026
# Version: v0.1


import time
from pymata4 import pymata4

import config
from config import *

# how long to sleep inside the poll busy-wait loop
pollSleepDelay = 0.005

# number of samples for the rolling average in poll_us
numSamples = 5

# delay between each sample so readings dont overlap
sampleInterval = 0.01

# fallback height if user doesnt enter a custom one
defaultOverHeightLimit = 4.0


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
                if (min == None and max == None):
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
                if (min == None and max == None):
                    return userInput
                elif (min <= userInput <= max):
                    return userInput
                else:
                    print(f"The value you entered must be between {min} and {max}.")
        except ValueError:
            print("The value you entered is invalid. Please enter a numerical value.")


def poll(pin, sonar=False):
    """
    Busywait until pollingRate seconds have passed then reads the pin
    Sonar flag switches between digital read and sonar read

    Takes:
        pin (int): arduino pin to read
        sonar (bool): if true reads sonar otherwise digital

    Returns:
        board read result - either digital_read or sonar_read output
    """
    original = time.time()

    while True:
        present = time.time()
        if (present - original) <= pollingRate:
            # not ready yet then sleep a bit before checking again
            time.sleep(pollSleepDelay)
        elif (present - original) > pollingRate:
            return board.digital_read(pin) if not sonar else board.sonar_read(pin)


def poll_us(pin, usNumber):
    """
    Poll  ultrasonic sensor numSamples times and average the results
    Check if the averaged height exceeds overheightLimit and updates state

    Takes:
        pin (int): trigger pin for the sonar
        usNumber (int): which sensor this is - used as the state dict key

    Returns:
        tuple: (bool overheight detected, float height in metres, str timestamp)
    """
    # take multiple samples and average to filter out noise
    samples = []
    for i in range(numSamples):
        raw = poll(pin, sonar=True)[0]
        samples.append(raw)
        time.sleep(sampleInterval)

    avgRaw = sum(samples) / len(samples)
    height = (sensorMountHeight * 100 - avgRaw) / 100
    result = height > overheightLimit

    if result:
        state[f"us{usNumber}"]["detected"] = True
        state[f"us{usNumber}"]["timeOfLast"] = time.time()
    else:
        state[f"us{usNumber}"]["detected"] = False

    return result, height, time.strftime("%X %x")


def get_over_height():
    """
    Prompts the user to optionally set a custom overheight limit.
    If they skip or enter N defaults to defaultOverHeightLimit.

    Takes:
        None

    Returns:
        overHeightLimit (float): the configured height threshold in metres
    """
    while True:
        enterHeightInput = input("Do you want to enter a custom over height limit? (Y/N) ").upper().replace(" ", "")

        if enterHeightInput == "Y":
            while True:
                overHeightLimit = read_float("Enter height for detection in m: ", 0, 5)
                print(f"Your over height limit is set at: {overHeightLimit} m")
                return overHeightLimit

        elif enterHeightInput == "N" or enterHeightInput == "":
            # no input or N - fall back to system default
            overHeightLimit = defaultOverHeightLimit
            print(f"Your height limit is set at: {overHeightLimit} m")
            return overHeightLimit

        else:
            print("Please enter Y or N.")