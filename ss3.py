
#SubSytem 3 H19
#Version: 8
#Last Edited: 08/05

from pymata4 import pymata4
import time
from utils import *
from config import *

#qPin declarations
tl6Green = 13
tl6Yellow = 12
tl6Red = 11
timer = 9 #result from NE556N (pin 5 on NE556N), will be a 0, 1, or none
trig = 2
echo5 = 3

global sequenceTl6Trigger

ss3Trigger = False
overHeightLimit = get_over_height()

def update(): 
    global ss3Trigger
    us5Result = poll_us(trig, echo5, overHeightLimit)
    ss3Trigger = us5Result[0]
    
    return us5Result, ss3Trigger


def set_tl(tlNumber, redPin, greenPin, yellowPin=None, colour="reset"):
    
    #set the state of this light to the colour
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
    try:
        board.set_pin_mode_digital_output(tl6Red)
        board.set_pin_mode_digital_output(tl6Yellow)
        board.set_pin_mode_digital_output(tl6Green)
        board.set_pin_mode_sonar(trig, echo5, timeout=200000)
        board.set_pin_mode_digital_output(timer)  # Set timer pin mode
        time.sleep(0.5)
        
        #default state
        set_tl(6, tl6Red, tl6Green, tl6Yellow, "red") #red on

        lastState = False
        while True:
            update()
            if ss3Trigger != lastState:
                if ss3Trigger:
                    #an overheight vehicle is detected by US5
                    print("Overheight vehicle detected by US5!")
                    set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")  # Turn everything OFF
                    set_tl(6, tl6Red, tl6Green, tl6Yellow, "green") # Green ON
                    time.sleep(5)
                    set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset") # Green OFF (all lights OFF)

                    update() 

                    if ss3Trigger:
                        #overheight vehicle still detected by US5
                        print("Overheight vehicle still detected by US5, TL6 flashing green!")
                        
                        # CRITICAL: Make sure red is OFF before starting flash
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")  # Explicitly turn ALL lights OFF
                        
                        #556 controls
                        timerStarted = False  
                        while ss3Trigger:
                            update()
                            
                            # Turn on 556 only once
                            if not timerStarted:
                                board.digital_write(timer, 1)
                                timerStarted = True
                            
                            time.sleep(0.01)
                        
                        
                        print("Overheight vehicle no longer detected by US5!")
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")  # All OFF
                        board.digital_write(timer, 0) #turn off 556
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "red") # Red ON

                    else:
                        print("Vehicle cleared from US5!")
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "yellow") #yellow on
                        time.sleep(3)
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset") #yellow off
                        set_tl(6, tl6Red, tl6Green, tl6Yellow, "red") #red on

            lastState = ss3Trigger
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nshutting down...")
        set_tl(6, tl6Red, tl6Green, tl6Yellow, "reset")
        board.shutdown()
        print("\nShutdown Complete")


#starting the program
if __name__ == "__main__":
    main()