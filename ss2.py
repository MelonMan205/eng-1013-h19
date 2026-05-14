# ss2.py
# Created by: Vincent Nguyen
# Created date: 14/05/2026
# Version: 1.0
# Description: Controls Subsystem 2 traffic lights, pedestrian lights,
#              button detection, cooldown timing, and 556 timer flashing.

from pymata4 import pymata4
import time

board = pymata4.Pymata4()

# Pin constants
pushButtonOnePin = 2
pushButtonTwoPin = 3

tl4GreenPin = 4
tl4YellowPin = 5
tl4RedPin = 6

tl5GreenPin = 7
tl5YellowPin = 8
tl5RedPin = 9

pedestrianGreenPin = 10
timerPowerPin = 11
solidRedPowerPin = 12

# Timing constants
tl4GreenTime = 20
tl4YellowTime = 3
tl5GreenTime = 10
tl5YellowTime = 3
pedestrianGreenTime = 3
pedestrianFlashTime = 2
cooldownTime = 30
buttonCheckInterval = 0.1

# Program variables
lastPedestrianTime = 0
lastButtonState = False


def setup_pins():
    """
    Sets the Arduino pin modes for all inputs and outputs.
    Parameters:
        None
    Returns:
        None
    """
    board.set_pin_mode_digital_input(pushButtonOnePin)
    board.set_pin_mode_digital_input(pushButtonTwoPin)

    board.set_pin_mode_digital_output(tl4GreenPin)
    board.set_pin_mode_digital_output(tl4YellowPin)
    board.set_pin_mode_digital_output(tl4RedPin)

    board.set_pin_mode_digital_output(tl5GreenPin)
    board.set_pin_mode_digital_output(tl5YellowPin)
    board.set_pin_mode_digital_output(tl5RedPin)

    board.set_pin_mode_digital_output(pedestrianGreenPin)
    board.set_pin_mode_digital_output(timerPowerPin)
    board.set_pin_mode_digital_output(solidRedPowerPin)


def set_pedestrian_solid_red():
    """
    Turns the pedestrian red light solid ON and disables the 556 timer.
    Parameters:
        None
    Returns:
        None
    """
    board.digital_write(pedestrianGreenPin, 0)
    board.digital_write(timerPowerPin, 0)
    board.digital_write(solidRedPowerPin, 1)


def set_pedestrian_flashing_red():
    """
    Turns the solid red path OFF and powers the 556 timer to flash red.
    Parameters:
        None
    Returns:
        None
    """
    board.digital_write(pedestrianGreenPin, 0)
    board.digital_write(solidRedPowerPin, 0)
    board.digital_write(timerPowerPin, 1)


def set_pedestrian_green():
    """
    Turns pedestrian green ON and disables all red pedestrian outputs.
    Parameters:
        None
    Returns:
        None
    """
    board.digital_write(pedestrianGreenPin, 1)
    board.digital_write(timerPowerPin, 0)
    board.digital_write(solidRedPowerPin, 0)


def set_tl4_green_tl5_red():
    """
    Sets TL4 to green and TL5 to red.
    Parameters:
        None
    Returns:
        None
    """
    board.digital_write(tl4GreenPin, 1)
    board.digital_write(tl4YellowPin, 0)
    board.digital_write(tl4RedPin, 0)

    board.digital_write(tl5GreenPin, 0)
    board.digital_write(tl5YellowPin, 0)
    board.digital_write(tl5RedPin, 1)


def set_tl4_yellow_tl5_red():
    """
    Sets TL4 to yellow and TL5 to red.
    Parameters:
        None
    Returns:
        None
    """
    board.digital_write(tl4GreenPin, 0)
    board.digital_write(tl4YellowPin, 1)
    board.digital_write(tl4RedPin, 0)

    board.digital_write(tl5GreenPin, 0)
    board.digital_write(tl5YellowPin, 0)
    board.digital_write(tl5RedPin, 1)


def set_tl4_red_tl5_green():
    """
    Sets TL4 to red and TL5 to green.
    Parameters:
        None
    Returns:
        None
    """
    board.digital_write(tl4GreenPin, 0)
    board.digital_write(tl4YellowPin, 0)
    board.digital_write(tl4RedPin, 1)

    board.digital_write(tl5GreenPin, 1)
    board.digital_write(tl5YellowPin, 0)
    board.digital_write(tl5RedPin, 0)


def set_tl4_red_tl5_yellow():
    """
    Sets TL4 to red and TL5 to yellow.
    Parameters:
        None
    Returns:
        None
    """
    board.digital_write(tl4GreenPin, 0)
    board.digital_write(tl4YellowPin, 0)
    board.digital_write(tl4RedPin, 1)

    board.digital_write(tl5GreenPin, 0)
    board.digital_write(tl5YellowPin, 1)
    board.digital_write(tl5RedPin, 0)


def button_was_pressed():
    """
    Detects a new button press from either pedestrian button.
    Parameters:
        None
    Returns:
        bool: True if a new button press is detected, otherwise False.
    """
    global lastButtonState

    currentButtonState = (
        board.digital_read(pushButtonOnePin)[0] == 1 or
        board.digital_read(pushButtonTwoPin)[0] == 1
    )

    if currentButtonState and not lastButtonState:
        lastButtonState = currentButtonState
        return True

    lastButtonState = currentButtonState
    return False


def check_button(signal):
    """
    Checks whether a pedestrian button has been pressed and whether cooldown has ended.
    Parameters:
        signal (string): The signal returned to decide which pedestrian sequence runs.
    Returns:
        string or None: Returns the signal if button press is accepted, otherwise None.
    """
    global lastPedestrianTime

    if button_was_pressed():
        if time.time() - lastPedestrianTime >= cooldownTime:
            print("Button pressed")
            return signal

        print("Cooldown active")

    return None


def wait_and_check_button(waitTime, signal):
    """
    Waits for a given time while repeatedly checking the pedestrian buttons.
    Parameters:
        waitTime (float): Number of seconds to wait.
        signal (string): Signal returned if an accepted button press occurs.
    Returns:
        string or None: Returns signal if accepted button press occurs, otherwise None.
    """
    startTime = time.time()

    while time.time() - startTime < waitTime:
        result = check_button(signal)

        if result is not None:
            return result

        time.sleep(buttonCheckInterval)

    return None


def run_pedestrian_sequence_from_tl4():
    """
    Runs the pedestrian sequence when TL4 was green or yellow.
    Parameters:
        None
    Returns:
        None
    """
    set_tl4_yellow_tl5_red()
    time.sleep(tl4YellowTime)

    board.digital_write(tl4YellowPin, 0)
    board.digital_write(tl4RedPin, 1)

    set_pedestrian_green()
    time.sleep(pedestrianGreenTime)

    set_pedestrian_flashing_red()
    time.sleep(pedestrianFlashTime)

    set_pedestrian_solid_red()


def run_pedestrian_sequence_from_tl5():
    """
    Runs the pedestrian sequence when TL5 was green or yellow.
    Parameters:
        None
    Returns:
        None
    """
    set_tl4_red_tl5_yellow()
    time.sleep(tl5YellowTime)

    board.digital_write(tl5YellowPin, 0)
    board.digital_write(tl5RedPin, 1)

    set_pedestrian_green()
    time.sleep(pedestrianGreenTime)

    set_pedestrian_flashing_red()
    time.sleep(pedestrianFlashTime)

    set_pedestrian_solid_red()


def run_normal_traffic_cycle():
    """
    Runs the normal TL4 and TL5 traffic sequence while checking pedestrian buttons.
    Parameters:
        None
    Returns:
        string: Returns RED_ON or RED_OFF depending on when the button was pressed.
    """
    while True:
        set_tl4_green_tl5_red()
        set_pedestrian_solid_red()

        result = wait_and_check_button(tl4GreenTime, "RED_ON")
        if result is not None:
            return result

        set_tl4_yellow_tl5_red()

        result = wait_and_check_button(tl4YellowTime, "RED_ON")
        if result is not None:
            return result

        set_tl4_red_tl5_green()
        set_pedestrian_solid_red()

        result = wait_and_check_button(tl5GreenTime, "RED_OFF")
        if result is not None:
            return result

        set_tl4_red_tl5_yellow()

        result = wait_and_check_button(tl5YellowTime, "RED_OFF")
        if result is not None:
            return result


def shutdown_outputs():
    """
    Turns all controlled pedestrian outputs OFF before shutting down the board.
    Parameters:
        None
    Returns:
        None
    """
    board.digital_write(pedestrianGreenPin, 0)
    board.digital_write(timerPowerPin, 0)
    board.digital_write(solidRedPowerPin, 0)


def main():
    """
    Main program loop for Subsystem 2.
    Parameters:
        None
    Returns:
        None
    """
    global lastPedestrianTime

    setup_pins()
    set_pedestrian_solid_red()

    while True:
        result = run_normal_traffic_cycle()

        if result == "RED_ON":
            run_pedestrian_sequence_from_tl4()
            lastPedestrianTime = time.time()

        elif result == "RED_OFF":
            run_pedestrian_sequence_from_tl5()
            lastPedestrianTime = time.time()


try:
    main()

except KeyboardInterrupt:
    shutdown_outputs()
    board.shutdown()