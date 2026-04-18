# Subsystem 1 Code
# Created By: Shreeneel Tarale
# Created Date: 14/04/2026
# Version: v0.1

import time
from pymata4 import pymata4
from utils import *
import config
from config import *



#pin declarations (solo)

us1Trig = 2
us1Echo = 3
us2Trig = 4
us2Echo = 5
timerReset = 6

#qPin declarations
tl1Red = 0
tl1Yellow = 1
tl1Green = 2
tl2Red = 3
tl2Yellow = 4
tl2Green = 5
pa1Enable = 6
wl1A = 7
wl1B = 8


global sequenceTl1Trigger, sequenceTl2Trigger, sequencePa1Trigger

sequenceTl1Trigger = False
sequenceTl2Trigger = False  
sequencePa1Trigger = False

#function declarations
def init():
    userInput = read_float("Enter the over height limit in metres (for default [4.0m], leave empty): ")
    overheightLimit = userInput if not (str(userInput).strip(" ")) == "" else 4.0

    board.set_pin_mode_sonar(us1Trig, us1Echo, timeout=200000)
    time.sleep(0.5)
    board.set_pin_mode_sonar(us2Trig, us2Echo, timeout=200000)
    time.sleep(0.5)

    
def shutdown():
    print("Shutting Down...")
    board.shutdown()

def set_tl(tlNumber, redPin, yellowPin, greenPin, colour="reset"):
    
    #set the state of this light to the colour
    state[f"tl{tlNumber}"]["colour"] = colour
    global redTimerTl1, yellowTimerTl1, redTimerTl2, yellowTimerTl2



    if colour == "red":

        if tlNumber == 1:
            redTimerTl1 = time.time()
        elif tlNumber == 2:
            redTimerTl2 = time.time()

        board.digital_write(redPin, 1)
        board.digital_write(yellowPin, 0)
        board.digital_write(greenPin, 0)
        
    if colour == "yellow":

        if tlNumber == 1:
            yellowTimerTl1 = time.time()
        elif tlNumber == 2:
            yellowTimerTl2 = time.time()

        board.digital_write(redPin, 0)
        board.digital_write(yellowPin, 1)
        board.digital_write(greenPin, 0)

    if colour == "green":

        board.digital_write(redPin, 0)
        board.digital_write(yellowPin, 0)
        board.digital_write(greenPin, 1)

    if colour == "reset":

        board.digital_write(redPin, 0)
        board.digital_write(yellowPin, 0)
        board.digital_write(greenPin, 0)


def sequence_tl1(start):

    global sequenceTl1Trigger
    now = start

    if not config.state["tl1"]["colour"] == "yellow":
        set_tl(1, tl1Red, tl1Yellow, tl1Green, "yellow")

    elif config.state["tl1"]["colour"] == "yellow" and (now-yellowTimerTl1 >= 1):
        set_tl(1, tl1Red, tl1Yellow, tl1Green, "red")
    
    elif config.state["tl1"]["colour"] == "red" and (now-redTimerTl1 >= 30):
        set_tl(1, tl1Red, tl1Yellow, tl1Green, "green")
        sequenceTl1Trigger = False


def sequence_tl2(start):

    global sequenceTl2Trigger
    now = start
    
    if not config.state["tl2"]["colour"] == "yellow":
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "yellow")

    elif config.state["tl2"]["colour"] == "yellow" and (now-yellowTimerTl2 >= 1):
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "red")
    
    elif config.state["tl2"]["colour"] == "red" and (now-redTimerTl2 >= 30):
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "green")
        sequenceTl2Trigger = False

def sequence_pa1(start):
    if not config.state["pa1"]["sound"]:
        board.digital_write(timerReset, 1)
        config.state["pa1"]["sound"] = True
    elif config.state["pa1"]["sound"] and not ((config.state["tl1"]["colour"] == "red") or (config.state["tl2"]["colour"] == "red")):
        board.digital_write(timerReset, 0)
        config.state["pa1"]["sound"] = False

        sequencePa1Trigger = False



def update():
    global sequenceTl1Trigger, sequenceTl2Trigger, sequencePa1Trigger

    current = time.time()

    us1Result = poll_us(us1Trig, 1)
    us2Result = poll_us(us2Trig, 2)

    if us1Result[0] and not config.state["us1"]["triggered"]:

        print(f"[ALERT] Overheight Vehicle Detected (US1), Height: {us1Result[1]:.2f}m, Time: {us1Result[2]}")

        config.state["us1"]["triggered"] = True 

        sequenceTl1Trigger = True
    
    if us2Result[0]:
        if config.state["us1"]["timeOfLast"] != None:
            if 16 <= (time.time() - config.state["us1"]["timeOfLast"]) <= 22.5:
                sequenceTl2Trigger = True
                sequencePa1Trigger = True
            else:
                sequenceTl2Trigger = True
                sequenceTl1Trigger = True

        
def main():
    
    try:

        init()

        set_tl(1, tl1Red, tl1Yellow, tl1Green, "green")
        set_tl(2, tl1Red, tl1Yellow, tl1Green, "green")

        while True:
            update()
            if sequenceTl1Trigger:
                sequence_tl1(start=time.time())
            if sequenceTl2Trigger:
                sequence_tl2(start=time.time())
            if sequencePa1Trigger:
                sequence_pa1(start=time.time())

    except KeyboardInterrupt:
        shutdown()    

if __name__ == "__main__":
    main()
