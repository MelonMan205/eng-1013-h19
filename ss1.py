# ss1.py
# Approach Height Detection Subsystem (Subsystem 1)
# Implements all required features and G2.
# Created By: Shreeneel Tarale
# Created Date: 14/04/2026
# Version: v4

import time
from pymata4 import pymata4
from utils import *
import config
from config import *
import output
from shift_register import process_shift_register

debug = True

# Pin declarations
us1Trig = 12
us1Echo = 13
us2Trig = 8
us2Echo = 9
timerReset = 11

tl1Red = 2
tl1Yellow = 3
tl1Green = 4
tl2Red = 5
tl2Yellow = 6
tl2Green = 7


testPin = 14

# Timing constants (seconds)
yellowDuration = 1
redDuration = 30

# Vehicle time thresholds (seconds) when highway speed over 500m
minTransitTime = 16
maxTransitTime = 22.5

# Sensor configuration constants
usSensorTimeout = 200000
usSensorInitDelay = 0.5

# Default overheight limit in metres
defaultOverheightLimit = 4.0

global sequenceTl1Trigger, sequenceTl2Trigger, sequencePa1Trigger

sequenceTl1Trigger = False
sequenceTl2Trigger = False
sequencePa1Trigger = False

redTimerTl1 = yellowTimerTl1 = redTimerTl2 = yellowTimerTl2 = 0.0


def init():
    """
    Initialise all output pins, ask the user for the overheight limit,
    and initialise the ultrasonic sensors.

    Parameters:
        None

    Returns:
        None
    """
    outputPins = [tl1Red, tl1Yellow, tl1Green, tl2Red, tl2Yellow, tl2Green, timerReset, testPin]
    for pin in outputPins:
        config.board.set_pin_mode_digital_output(pin)

    global overheightLimit
    overheightLimit = defaultOverheightLimit

    if not config.powerLoss:
        while True:
            try:
                userInput = str(input(f"Enter the over height limit in metres (for default [{defaultOverheightLimit}m], leave empty): "))

                if userInput.strip(" ") == "":
                    overheightLimit = defaultOverheightLimit
                    break
                else:
                    userInput = float(userInput)
                    overheightLimit = userInput
                    break
            except ValueError:
                print("Either leave this empty or enter a numerical value.")

    

        
    
    
    config.board.set_pin_mode_sonar(us1Trig, us1Echo, timeout=usSensorTimeout)
    
    time.sleep(usSensorInitDelay)
    
    config.board.set_pin_mode_sonar(us2Trig, us2Echo, timeout=usSensorTimeout)
    


def shutdown():
    """
    Shuts down the Arduino cleanly

    Parameters:
        None

    Returns:
        None
    """
    print("Shutting Down...")
    config.board.shutdown()


def set_tl(tlNumber, redPin, yellowPin, greenPin, colour="reset"):
    """
    Sets the chosen traffic light to the given colour and records the time
    at which red or yellow was set

    Parameters:
        tlNumber (int): The traffic light identifier (1 or 2)
        redPin (int): Arduino pin number of red 
        yellowPin (int): Arduino pin number of yellow 
        greenPin (int): Arduino pin number of green led 
        colour (string): Target colour (also has "reset" key, turns off led)

    Returns:
        None
    """
    # Update the system state with the new colour
    state[f"tl{tlNumber}"]["colour"] = colour
    global redTimerTl1, yellowTimerTl1, redTimerTl2, yellowTimerTl2

    if colour == "red":
        if tlNumber == 1:
            redTimerTl1 = time.time()
        elif tlNumber == 2:
            redTimerTl2 = time.time()

        output.write(redPin, 1)
        output.write(yellowPin, 0)
        output.write(greenPin, 0)

    if colour == "yellow":
        if tlNumber == 1:
            yellowTimerTl1 = time.time()
        elif tlNumber == 2:
            yellowTimerTl2 = time.time()

        output.write(redPin, 0)
        output.write(yellowPin, 1)
        output.write(greenPin, 0)

    if colour == "green":
        output.write(redPin, 0)
        output.write(yellowPin, 0)
        output.write(greenPin, 1)

    if colour == "reset":
        output.write(redPin, 0)
        output.write(yellowPin, 0)
        output.write(greenPin, 0)


def sequence_tl1(start):
    """
    Initiates TL1 through overheight response sequence:
    green > yellow 1s > red 30s > green.

    Parameters:
        start (float): The current timestamp from time.time()

    Returns:
        None
    """
    global sequenceTl1Trigger
    now = start

    if config.state["tl1"]["colour"] == "green":
        set_tl(1, tl1Red, tl1Yellow, tl1Green, "yellow")

    elif config.state["tl1"]["colour"] == "yellow" and (now - yellowTimerTl1 >= yellowDuration):
        set_tl(1, tl1Red, tl1Yellow, tl1Green, "red")

    elif config.state["tl1"]["colour"] == "red" and (now - redTimerTl1 >= redDuration):
        set_tl(1, tl1Red, tl1Yellow, tl1Green, "green")
        config.state["us1"]["triggered"] = False
        sequenceTl1Trigger = False


def sequence_tl2(start):
    """
    Initiates TL2 through overheight response sequence:
    green > yellow 1s > red 30s > green.

    Parameters:
        start (float): The current timestamp from time.time()

    Returns:
        None
    """
    global sequenceTl2Trigger
    now = start

    if config.state["tl2"]["colour"] == "green":
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "yellow")

    elif config.state["tl2"]["colour"] == "yellow" and (now - yellowTimerTl2 >= yellowDuration):
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "red")

    elif config.state["tl2"]["colour"] == "red" and (now - redTimerTl2 >= redDuration):
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "green")
        sequenceTl2Trigger = False


def sequence_pa1(start):
    """
    Activates PA1 buzzer when either TL1/TL2 is red and deactivates once both lights return to green

    Parameters:
        start (float): The current timestamp from time.time()

    Returns:
        None
    """
    global sequencePa1Trigger

    if not config.state["pa1"]["sound"]:
        output.write(timerReset, 1)
        config.state["pa1"]["sound"] = True
    elif config.state["pa1"]["sound"] and not (
        (config.state["tl1"]["colour"] == "red") or
        (config.state["tl2"]["colour"] == "red")
    ):
        output.write(timerReset, 0)
        config.state["pa1"]["sound"] = False
        sequencePa1Trigger = False


def update():
    """
    Polls US1/US2 for overheight detections and sets the appropriate
    sequence trigger flags based on result

    Parameters:
        None

    Returns:
        None
    """
    global sequenceTl1Trigger, sequenceTl2Trigger, sequencePa1Trigger

    us1Result = poll_us(us1Trig, 1)
    us2Result = poll_us(us2Trig, 2)

    #  TL1 sequence if US1 detects overheight vehicle for first time
    if us1Result[0] and not config.state["us1"]["triggered"]:
        print(f"[ALERT] Overheight Vehicle Detected (US1), "
              f"Height: {us1Result[1]:.2f}m, Time: {us1Result[2]}")

        config.state["us1"]["triggered"] = True
        sequenceTl1Trigger = True

    if us2Result[0]:
        if config.state["us1"]["timeOfLast"] is not None:
            timeSinceUs1 = time.time() - config.state["us1"]["timeOfLast"]

            # Same detected US2 reading in time range
            if minTransitTime <= timeSinceUs1 <= maxTransitTime:
                sequenceTl2Trigger = True
                sequencePa1Trigger = True

            # Vehicle detected only by US2 (US1 detection was too long ago)
            elif timeSinceUs1 > maxTransitTime:
                sequencePa1Trigger = True
                sequenceTl2Trigger = True
                config.state["us1"]["triggered"] = True
                sequenceTl1Trigger = True
        else:
            # US1 not triggered earlier
            sequencePa1Trigger = True
            sequenceTl2Trigger = True
            config.state["us1"]["triggered"] = True
            sequenceTl1Trigger = True


def run_ss1():
    """
    Main execution loop for Subsystem 1 - handles powerloss recovery,
    calls update() to poll sensors, and runs active sequences from trigger flags

    Parameters:
        None

    Returns:
        None
    """
    try:
        # Restore lights to green after a power loss event
        if config.powerLoss:
            config.powerLoss = False
            set_tl(1, tl1Red, tl1Yellow, tl1Green, "green")
            set_tl(2, tl2Red, tl2Yellow, tl2Green, "green")

        update()

        if sequenceTl1Trigger:
            sequence_tl1(start=time.time())
        if sequenceTl2Trigger:
            sequence_tl2(start=time.time())
        if sequencePa1Trigger:
            sequence_pa1(start=time.time())

        #test a pin to see if arduino still has power
        config.board.digital_write(testPin, 1)
        process_shift_register(config.state)
    #handle powerloss
    except RuntimeError:
                config.powerLoss = True
                power_loss()

def power_loss():
    while True:
        try:
            # Rebuild the board connection then re-setup pins
            config.board = pymata4.Pymata4()
            time.sleep(2)
            
            output.output_init()
            
            init()
            

            # Reset all sequence state so no stale triggers fire on resume
            global sequenceTl1Trigger, sequenceTl2Trigger, sequencePa1Trigger
            sequenceTl1Trigger = False
            sequenceTl2Trigger = False
            sequencePa1Trigger = False
            config.state["us1"]["triggered"] = False
            config.state["pa1"]["sound"] = False
            config.powerLoss = False

            # Restore both lights to green
            set_tl(1, tl1Red, tl1Yellow, tl1Green, "green")
            set_tl(2, tl2Red, tl2Yellow, tl2Green, "green")

            
            break
        
        #handle the case that arduino still doesnt have power
        except RuntimeError:
            
            try:
                config.board.serial_port.close()
            except RuntimeError:
                pass
            time.sleep(1)
            pass

def main():
    """
    Entry point for Subsystem 1 - Initialises, sets both TL to green then run the subsystem loop. Exception handling.

    Parameters:
        None

    Returns:
        None
    """
    try:
        output.output_init()
        init()

        set_tl(1, tl1Red, tl1Yellow, tl1Green, "green")
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "green")

        while True:
            run_ss1()
            
            

    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()