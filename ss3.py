# ss3.py
# Subsystem 3 - over-height exit control
# handles US5 detection and TL6 sequencing including 556 timer flash
# Created By : H19
# Created Date: 08/05/2026
# version ='8.0'

from pymata4 import pymata4
import time
from utils import *
from config import *

# pin declarations
tl6Green = 13
tl6Yellow = 12
tl6Red = 11
timer = 9  # result from NE556N (pin 5 on NE556N) - outputs 0 1 or none
trig = 2
echo5 = 3

# timing constants
sonarTimeout = 200000
sonarInitDelay = 0.5
greenDuration = 5      # how long tl6 stays green before checking if vehicle cleared
yellowDuration = 3     # yellow phase duration
flashLoopDelay = 0.01  # poll rate inside the 556 flash loop
loopDelay = 0.05       # main loop poll rate

global sequenceTl6Trigger

ss3Trigger = False
overHeightLimit = get_over_height()

def poll_us(pin, usNumber, overHeightLimit):
    """
    Poll  ultrasonic sensor numSamples times and average the results
    Check if the averaged height exceeds overheightLimit and updates state

    Takes:
        pin (int): trigger pin for the sonar
        usNumber (int): which sensor this is - used as the state dict key
        overHeightLimit (int): the overheight detection limit

    Returns:
        tuple: (bool overheight detected, float height in metres, str timestamp)
    """
    distance = poll(pin, sonar=True)[0]
    height = (sensorMountHeight*100 - distance)/100
    result = height > overHeightLimit
    if result:
        state[f"us{usNumber}"]["detected"] = True 
        state[f"us{usNumber}"]["timeOfLast"] = time.time()
        
    else:
        state[f"us{usNumber}"]["detected"] = False

    return result, height, time.strftime("%x")


def update():
    """
    Polls US5 + update ss3Trigger
    return  raw sensor result and trigger state

    Parameters:
        None

    Returns:
        tuple: (us5Result tuple from poll_us, bool ss3Trigger)
    """
    global ss3Trigger
    us5Result = poll_us(trig, echo5, overHeightLimit)
    ss3Trigger = us5Result[0]

    return us5Result, ss3Trigger


def set_tl(tlNumber, redPin, greenPin, yellowPin=None, colour="reset"):
    """
    Sets traffic light to given color by setting its pins
    updates state dict so other subsystems can check whats happening
    

    Parameters:
        tlNumber (int): which traffic light eg 6
        redPin (int): arduino pin for red
        greenPin (int): arduino pin for green
        yellowPin (int or None): arduino pin for yellow if present
        colour (str): target colour: red yellow green or reset

    Returns:
        None
    """
    # update state so other subsystems can read current colour
    state[f"tl{tlNumber}"]["colour"] = colour

    if colour == "red":
        board.digital_write(redPin, 1)
        if yellowPin is not None:
            board.digital_write(yellowPin, 0)
        board.digital_write(greenPin, 0)

    elif colour == "yellow":
        if yellowPin is None:
            print(f"Warning: TL{tlNumber} has no yellow light")
            return
        board.digital_write(redPin, 0)
        board.digital_write(yellowPin, 1)
        board.digital_write(greenPin, 0)

    elif colour == "green":
        board.digital_write(redPin, 0)
        if yellowPin is not None:
            board.digital_write(yellowPin, 0)
        board.digital_write(greenPin, 1)

    elif colour == "reset":
        board.digital_write(redPin, 0)
        if yellowPin is not None:
            board.digital_write(yellowPin, 0)
        board.digital_write(greenPin, 0)


def main():
    """
    Entry point for subsystem 3 set up pins and loop check US5
    when overheight detected runs green sequence then checks if vehicle cleared
    If still there then flashing control handed to the 556 timer
    Shuts down cleanly on keyboard interrupt

    Parameters:
        None

    Returns:
        None
    """
    try:
        board.set_pin_mode_digital_output(tl6Red)
        board.set_pin_mode_digital_output(tl6Yellow)
        board.set_pin_mode_digital_output(tl6Green)
        board.set_pin_mode_sonar(trig, echo5, timeout=sonarTimeout)
        board.set_pin_mode_digital_output(timer)
        time.sleep(sonarInitDelay)

        # default state is red and exit is closed until vehicle detected
        set_tl(6, tl6Red, tl6Green, tl6Yellow, "red")

        lastState = False
        while True:
            update()

            # only act on state changes not every loop tick
            if ss3Trigger != lastState:
                if ss3Trigger:
                    # overheight vehicle detected and open the exit
                    print("Overheight vehicle detected by US5!")
                    set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")  # clear before switching
                    set_tl(6, tl6Red, tl6Green, tl6Yellow, "green")
                    time.sleep(greenDuration)
                    set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")

                    update()

                    if ss3Trigger:
                        # vehicle still there after green then hand flash duty to 556
                        print("Overheight vehicle still detected by US5, TL6 flashing green!")

                        # make sure red is fully off before 556 takes over green
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")

                        timerStarted = False
                        while ss3Trigger:
                            update()

                            # only enable 556 once
                            if not timerStarted:
                                board.digital_write(timer, 1)
                                timerStarted = True

                            time.sleep(flashLoopDelay)

                        # vehicle cleared then stop 556 and go back to red
                        print("Overheight vehicle no longer detected by US5!")
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")
                        board.digital_write(timer, 0)
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "red")

                    else:
                        # vehicle cleared before green ran out then normal yellow then red
                        print("Vehicle cleared from US5!")
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "yellow")
                        time.sleep(yellowDuration)
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "red")

            lastState = ss3Trigger
            time.sleep(loopDelay)

    except KeyboardInterrupt:
        print("\nShutting down...")
        set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")
        board.shutdown()
        print("\nShutdown complete")


if __name__ == "__main__":
    main()