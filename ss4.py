from pymata4 import pymata4
import time
from utils import *
import config
from config import *


tolerance = 2

#ultrasonics
trig3 = 4
echo3 =5
trig4 = 2
echo4 = 3

#leds
tl3Green = 11
tl3Yellow = 12
tl3Red = 13
tl1Green= 12
tl1Yellow=12
tl1Red= 10
tl2Green=12
tl2Yellow=12
tl2Red= 9

#warning lights
wl1One = 8
wl1Two = 7

#buzzer
pa1= 6            

# TL1
board.set_pin_mode_digital_output(tl1Red)
board.set_pin_mode_digital_output(tl1Yellow)
board.set_pin_mode_digital_output(tl1Green)

# TL2
board.set_pin_mode_digital_output(tl2Red)
board.set_pin_mode_digital_output(tl2Yellow)
board.set_pin_mode_digital_output(tl2Green)

# TL3
board.set_pin_mode_digital_output(tl3Red)
board.set_pin_mode_digital_output(tl3Yellow)
board.set_pin_mode_digital_output(tl3Green)

# Warning lights
board.set_pin_mode_digital_output(wl1One)
board.set_pin_mode_digital_output(wl1Two)

# Buzzer
board.set_pin_mode_digital_output(pa1)
               
overHeightLimit = get_over_height()

global sequenceTl3Trigger

ss4Trigger = False

def poll_us(pin, usNumber, overHeightLimit):
    distance = poll(pin, sonar=True)[0] 
    height = (sensorMountHeight*100 - distance)/100
    result = height > overHeightLimit
    print(usNumber, height)
    if result:
        state[f"us{usNumber}"]["detected"] = True 
        state[f"us{usNumber}"]["timeOfLast"] = time.time()
        
    else:
        state[f"us{usNumber}"]["detected"] = False

    return result, height, time.strftime("%x")

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

def set_wl(wlNumber, pin1, pin2, mode="reset"):
    
    #set the state of this light to the colour
    state[f"wl{wlNumber}"]["mode"] = mode

    if mode == "on":
        board.digital_write(pin1, 1)
        board.digital_write(pin2, 1)

    elif mode == "off":
        board.digital_write(pin1, 0)
        board.digital_write(pin2, 0)
        
    elif mode == "reset":

        board.digital_write(pin1, 0)
        board.digital_write(pin2, 0)



def update():
    global ss4Trigger

    us3Result = poll_us(trig3, 3, overHeightLimit)
    us4Result = poll_us(trig4, 4, overHeightLimit)

    ss4Trigger = abs(us3Result[1]-us4Result[1]) <= tolerance and us3Result[0]

    
def main():
    try:
        board.set_pin_mode_sonar(trig3, echo3, timeout=200000)
        time.sleep(0.5)
        board.set_pin_mode_sonar(trig4, echo4, timeout=200000)
        time.sleep(0.5)

        set_tl(3, tl3Red, tl3Green, tl3Yellow, "green")

        update()
        while True:
            update()

            if ss4Trigger:

                # turn traffic lights red
                set_tl(3, tl3Red, tl3Green, tl3Yellow, "red")
                set_tl(2, tl2Red, tl2Green, tl2Yellow, "red")
                set_tl(1, tl1Red, tl1Green, tl1Yellow, "red")

                board.digital_write(pa1, 1)

                # keep flashing while overheight exists
                while ss4Trigger:
                    update()

                    set_wl(1, wl1One, wl1Two, "on")
                    time.sleep(0.075)

                    update()

                    set_wl(1, wl1One, wl1Two, "off")
                    time.sleep(0.075)

                # reset AFTER loop exits
                set_wl(1, wl1One, wl1Two, "off")

                set_tl(1, tl1Red, tl1Green, tl1Yellow, "reset")
                set_tl(2, tl2Red, tl2Green, tl2Yellow, "reset")
                set_tl(3, tl3Red, tl3Green, tl3Yellow, "green")

                board.digital_write(pa1, 0)

            time.sleep(0.05)


    except KeyboardInterrupt:
        print("Shutting down...")
        set_tl(1, tl1Red, tl1Green, tl1Yellow, "reset")
        set_tl(2, tl2Red, tl2Green, tl2Yellow, "reset")
        set_tl(3, tl3Red, tl3Green, tl3Yellow, "reset")
        set_wl(1,wl1One,wl1Two, "off")
        board.shutdown()
        print("Shutdown complete")

if __name__ == "__main__":
    main()