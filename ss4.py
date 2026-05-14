# ss4.py
# Tunnel height detection subsystem (subsystem 4)
# handles US3/US4 ultrasonic sensors TL3 and WL2
# Created By : Tim
# Created Date: 13/04/2026
# version: v3

from pymata4 import pymata4
import time
from utils import *
import config
from config import *

# how close us3 and us4 readings need to be to count as same vehicle
tolerance = 0.02

# sonar init delay so sensor has time to settle
sonarInitDelay = 0.5

# main loop poll rate - keeps things responsive without hammering the board
loopDelay = 0.05

# sonar timeout in microseconds
sonarTimeout = 200000

# ultrasonics
trig3 = 2
echo3 = 3
trig4 = 8
echo4 = 9

# traffic light 3 pins
tl3Red = 13
tl3Yellow = 12
tl3Green = 11

# warning light 2 and the transistor that enables it
wl2 = 6
enablerTransistor = 7


# setup tl3
board.set_pin_mode_digital_output(tl3Red)
board.set_pin_mode_digital_output(tl3Yellow)
board.set_pin_mode_digital_output(tl3Green)

# setup wl2 and its enabler
board.set_pin_mode_digital_output(wl2)
board.set_pin_mode_digital_output(enablerTransistor)

board.digital_write(wl2, 0)
board.digital_write(enablerTransistor, 0)

try:
    overHeightLimit = get_over_height()

except KeyboardInterrupt:
    print("\nShutting down...")
    board.shutdown()
    print("\nShutdown complete")

global sequenceTl3Trigger

ss4Trigger = False


def poll_us(pin, usNumber, overHeightLimit):
    """
    Polls a ultrasonic sensor and check if detected is overheight
    updates shared state dict with result and timestamp

    Parameters:
        pin (int): trigger pin for the sonar
        usNumber (int): which sensor this is, 3 or 4, used for state key
        overHeightLimit (float): height threshold in metres

    Returns:
        tuple: (bool overheight result - float height in metres - str datestring)
    """
    distance = poll(pin, sonar=True)[0]
    height = (sensorMountHeight * 100 - distance) / 100
    result = height > overHeightLimit

    if result:
        state[f"us{usNumber}"]["detected"] = True
        state[f"us{usNumber}"]["timeOfLast"] = time.time()
    else:
        state[f"us{usNumber}"]["detected"] = False

    return result, height, time.strftime("%x")


def set_tl(tlNumber, redPin, greenPin, yellowPin=None, colour="reset"):
    """
    Sets traffic light to given color by setting its pins
    updates state dict so other subsystems can check whats happening

    Parameters:
        tlNumber (int): which traffic light eg 3
        redPin (int): arduino pin for red led
        greenPin (int): arduino pin for green led
        yellowPin (int or None): arduino pin for yellow led if it has one
        colour (str): target colour: red yellow green or reset

    Returns:
        None
    """
    # update shared state so other subsystemscan see current colour
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


def set_wl(wlNumber, pin, mode="reset"):
    """
    Sets a warning light to on off or reset
    resets and off both turn off the pin reset also clears state.

    Parameters:
        wlNumber (int): which warning light eg 2
        pin (int): arduino pin for the warning light
        mode (str): on off or reset

    Returns:
        None
    """
    # track mode in state for other subsystems
    state[f"wl{wlNumber}"]["mode"] = mode

    if mode == "on":
        board.digital_write(pin, 1)
    elif mode == "off":
        board.digital_write(pin, 0)
    elif mode == "reset":
        board.digital_write(pin, 0)


def update():
    """
    Polls both ultrasonic sensors and sets ss4Trigger flag
    ss4Trigger flag is only true if both sensors agree within tolerance AND us3 sees overheight

    Parameters:
        None

    Returns:
        None
    """
    global ss4Trigger

    us3Result = poll_us(trig3, 3, overHeightLimit)
    us4Result = poll_us(trig4, 4, overHeightLimit)

    # us4 verifies us3 - readings must be within tolerance to count
    ss4Trigger = abs(us3Result[1] - us4Result[1]) <= tolerance and us3Result[0]


def main():
    """
    Entry point for subsystem 4 set up sonars then loop checking overheight vehicles.
    Turn TL3 red and enable WL2 flashing while overheight is detected
    reset everything when we want to clear and shuts down cleanly on keyboard interrupt

    Parameters:
        None

    Returns:
        None
    """
    try:
        board.set_pin_mode_sonar(trig3, echo3, timeout=sonarTimeout)
        time.sleep(sonarInitDelay)
        board.set_pin_mode_sonar(trig4, echo4, timeout=sonarTimeout)
        time.sleep(sonarInitDelay)

        # start green - normal state
        set_tl(3, tl3Red, tl3Green, tl3Yellow, "green")

        update()
        while True:
            update()

            if ss4Trigger:
                # overheight detected - go red and enable wl2
                set_tl(3, tl3Red, tl3Green, tl3Yellow, "red")
                board.digital_write(enablerTransistor, 1)
                set_wl(2, wl2, "on")

                # hold red and keep wl2 on until vehicle clears
                while ss4Trigger:
                    update()
                    board.digital_write(enablerTransistor, 1)
                    set_wl(2, wl2, "on")

                # vehicle gone - reset everything back to normal
                board.digital_write(enablerTransistor, 0)
                set_wl(2, wl2, "off")
                set_tl(3, tl3Red, tl3Green, tl3Yellow, "green")

            time.sleep(loopDelay)

    except KeyboardInterrupt:
        print("Shutting down...")
        set_tl(3, tl3Red, tl3Green, tl3Yellow, "reset")
        board.digital_write(enablerTransistor, 0)
        set_wl(2, wl2, "reset")
        board.shutdown()
        print("Shutdown complete")


if __name__ == "__main__":
    main()