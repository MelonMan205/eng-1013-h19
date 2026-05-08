# Subsystem 1 Code
# Created By: Shreeneel Tarale
# Created Date: 14/04/2026
# Version: v0.1

import time
from pymata4 import pymata4
from utils import *
import config
from config import *
import output
from shift_register import process_shift_register

debug = True


#pin declarations (solo)

us1Trig = 12 
us1Echo = 13
us2Trig = 8 #8 (12 for testing)
us2Echo = 9 #9 (13 for testing)
timerReset = 11

#qPin declarations
tl1Red = 2
tl1Yellow = 3
tl1Green = 4
tl2Red = 5
tl2Yellow = 6
tl2Green = 7
pa1Enable = 11
wl1A = 9
wl1B = 10




global sequenceTl1Trigger, sequenceTl2Trigger, sequencePa1Trigger

sequenceTl1Trigger = False
sequenceTl2Trigger = False  
sequencePa1Trigger = False

redTimerTl1 = yellowTimerTl1 = redTimerTl2 = yellowTimerTl2 = 0.0

#function declarations
def init():

    init = [tl1Red, tl1Yellow, tl1Green, tl2Red, tl2Yellow, tl2Green, pa1Enable, wl1A, wl1B]
    for i in init:
        board.set_pin_mode_digital_output(i)
    

    while True:
        try:

            userInput = str(input("Enter the over height limit in metres (for default [4.0m], leave empty): "))

            if userInput.strip(" ") == "":
                break
            else:
                userInput = float(userInput)
                break
        except ValueError:
            print("Either leave this empty or enter a numerical value.")
                              

    global overheightLimit
    overheightLimit = userInput if not (str(userInput).strip(" ")) == "" else 4.0

    board.set_pin_mode_sonar(us1Trig, us1Echo, timeout=200000)
    time.sleep(0.5)
    board.set_pin_mode_sonar(us2Trig, us2Echo, timeout=200000)
    time.sleep(0.5) # (disabled for tesintg)

    
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

    global sequenceTl1Trigger
    now = start

    if config.state["tl1"]["colour"] == "green":
        set_tl(1, tl1Red, tl1Yellow, tl1Green, "yellow")

    elif config.state["tl1"]["colour"] == "yellow" and (now-yellowTimerTl1 >= 1):
        set_tl(1, tl1Red, tl1Yellow, tl1Green, "red")
    
    elif config.state["tl1"]["colour"] == "red" and (now-redTimerTl1 >= 3):
        set_tl(1, tl1Red, tl1Yellow, tl1Green, "green")
        config.state["us1"]["triggered"] = False
        sequenceTl1Trigger = False


def sequence_tl2(start):

    global sequenceTl2Trigger
    now = start
    
    if config.state["tl2"]["colour"] == "green":
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "yellow")

    elif config.state["tl2"]["colour"] == "yellow" and (now-yellowTimerTl2 >= 1):
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "red")
    
    elif config.state["tl2"]["colour"] == "red" and (now-redTimerTl2 >= 3):
        set_tl(2, tl2Red, tl2Yellow, tl2Green, "green")
        sequenceTl2Trigger = False

def sequence_pa1(start):
    global sequencePa1Trigger

    if not config.state["pa1"]["sound"]:
        output.write(timerReset, 1)
        config.state["pa1"]["sound"] = True
    elif config.state["pa1"]["sound"] and not ((config.state["tl1"]["colour"] == "red") or (config.state["tl2"]["colour"] == "red")):
        output.write(timerReset, 0)
        config.state["pa1"]["sound"] = False

        sequencePa1Trigger = False



def update():
    global sequenceTl1Trigger, sequenceTl2Trigger, sequencePa1Trigger

    us1Result = poll_us(us1Trig, 1)
    us2Result = poll_us(us2Trig, 2)

    if us1Result[0] and not config.state["us1"]["triggered"]:

        print(f"[ALERT] Overheight Vehicle Detected (US1), Height: {us1Result[1]:.2f}m, Time: {us1Result[2]}")

        config.state["us1"]["triggered"] = True 

        sequenceTl1Trigger = True
        
    
    if us2Result[0]:
        #debug
        #print(f"[DEBUG] Overheight Vehicle Detected (US2), Height: {us2Result[1]:.2f}m, Time: {us2Result[2]} time since US1: {time.time() - config.state['us1']['timeOfLast']:.2f}") if debug else None
        if config.state["us1"]["timeOfLast"] != None:
            # ACTUAL: if 16 <= (time.time() - config.state["us1"]["timeOfLast"]) <= 22.5:
            if 5 <= (time.time() - config.state["us1"]["timeOfLast"]) <= 10:
                sequenceTl2Trigger = True
                sequencePa1Trigger = True
            elif time.time() - config.state["us1"]["timeOfLast"] > 10:
                sequencePa1Trigger = True
                sequenceTl2Trigger = True
                config.state["us1"]["triggered"] = True
                sequenceTl1Trigger = True
        else:
            sequencePa1Trigger = True
            sequenceTl2Trigger = True
            config.state["us1"]["triggered"] = True
            sequenceTl1Trigger = True

def run_ss1():
    update()
    if sequenceTl1Trigger:
        sequence_tl1(start=time.time())
    if sequenceTl2Trigger:
        sequence_tl2(start=time.time())
    if sequencePa1Trigger:
        sequence_pa1(start=time.time())
    process_shift_register(config.state) 
        
def main():
    
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
