# Subsystem 2 Code
# Created By: [Name]
# Created Date: [Date]
# Version: v0.2

import time
from pymata4 import pymata4
from utils import *
import config
from config import *
import output
from shift_register import process_shift_register

# direct pin declarations
pb1 = 6
pb2 = 7

# qPin declarations
tl4Red = 12
tl4Yellow = 13
tl4Green = 14
tl5Red = 15
tl5Yellow = 16
tl5Green = 17
pl1Red = 18
pl1Green = 19
pl2Red = 20
pl2Green = 21
timerEnable = 22

global cyclePhase, cycleTimer, pedPhase, pedTimer, lastPedTime, pbPrinted

cyclePhase = "tl4Green"
cycleTimer = 0.0
pedPhase = None
pedTimer = 0.0
lastPedTime = -30.0
pbPrinted = False


def init():
    board.set_pin_mode_digital_input(pb1)
    board.set_pin_mode_digital_input(pb2)
    set_tl(4, tl4Red, tl4Yellow, tl4Green, "green")
    set_tl(5, tl5Red, tl5Yellow, tl5Green, "red")
    set_pl("red")
    global cycleTimer
    cycleTimer = time.time()


def shutdown():
    print("Shutting down...")
    board.shutdown()


def set_tl(tlNumber, redPin, yellowPin, greenPin, colour="reset"):
    config.state[f"tl{tlNumber}"]["colour"] = colour
    if colour == "red":
        output.write(redPin, 1)
        output.write(yellowPin, 0)
        output.write(greenPin, 0)
    elif colour == "yellow":
        output.write(redPin, 0)
        output.write(yellowPin, 1)
        output.write(greenPin, 0)
    elif colour == "green":
        output.write(redPin, 0)
        output.write(yellowPin, 0)
        output.write(greenPin, 1)
    else:
        output.write(redPin, 0)
        output.write(yellowPin, 0)
        output.write(greenPin, 0)


def set_pl(colour="reset"):
    output.write(timerEnable, 1 if colour == "flash" else 0)
    output.write(pl1Green, 1 if colour == "green" else 0)
    output.write(pl2Green, 1 if colour == "green" else 0)
    output.write(pl1Red, 1 if colour == "red" else 0)
    output.write(pl2Red, 1 if colour == "red" else 0)


def cycle_tl(now):
    global cyclePhase, cycleTimer
    if cyclePhase == "tl4Green" and (now - cycleTimer) >= 20:
        set_tl(4, tl4Red, tl4Yellow, tl4Green, "yellow")
        cyclePhase = "tl4Yellow"
        cycleTimer = now
    elif cyclePhase == "tl4Yellow" and (now - cycleTimer) >= 3:
        set_tl(4, tl4Red, tl4Yellow, tl4Green, "red")
        set_tl(5, tl5Red, tl5Yellow, tl5Green, "green")
        cyclePhase = "tl5Green"
        cycleTimer = now
    elif cyclePhase == "tl5Green" and (now - cycleTimer) >= 10:
        set_tl(5, tl5Red, tl5Yellow, tl5Green, "yellow")
        cyclePhase = "tl5Yellow"
        cycleTimer = now
    elif cyclePhase == "tl5Yellow" and (now - cycleTimer) >= 3:
        set_tl(5, tl5Red, tl5Yellow, tl5Green, "red")
        set_tl(4, tl4Red, tl4Yellow, tl4Green, "green")
        cyclePhase = "tl4Green"
        cycleTimer = now


def sequence_ped(now):
    global pedPhase, pedTimer, cyclePhase, cycleTimer, lastPedTime, pbPrinted
    if pedPhase == "pedWait" and (now - pedTimer) >= 2:
        if config.state["tl5"]["colour"] != "red":
            set_tl(5, tl5Red, tl5Yellow, tl5Green, "yellow")
            pedPhase = "tl5Yellow"
        else:
            set_tl(4, tl4Red, tl4Yellow, tl4Green, "yellow")
            pedPhase = "tl4Yellow"
        pedTimer = now
    elif pedPhase == "tl5Yellow" and (now - pedTimer) >= 3:
        set_tl(5, tl5Red, tl5Yellow, tl5Green, "red")
        set_tl(4, tl4Red, tl4Yellow, tl4Green, "yellow")
        pedPhase = "tl4Yellow"
        pedTimer = now
    elif pedPhase == "tl4Yellow" and (now - pedTimer) >= 3:
        set_tl(4, tl4Red, tl4Yellow, tl4Green, "red")
        set_pl("green")
        pedPhase = "plGreen"
        pedTimer = now
    elif pedPhase == "plGreen" and (now - pedTimer) >= 3:
        set_pl("flash")
        pedPhase = "plFlash"
        pedTimer = now
    elif pedPhase == "plFlash" and (now - pedTimer) >= 2:
        set_pl("red")
        set_tl(4, tl4Red, tl4Yellow, tl4Green, "green")
        lastPedTime = now
        pbPrinted = False
        pedPhase = None
        cyclePhase = "tl4Green"
        cycleTimer = now


def sequence_us5(now):
    global pedPhase, pedTimer, cyclePhase, cycleTimer
    if pedPhase == "us5Stop4" and (now - pedTimer) >= 3:
        set_tl(4, tl4Red, tl4Yellow, tl4Green, "red")
        if config.state["tl5"]["colour"] != "red":
            set_tl(5, tl5Red, tl5Yellow, tl5Green, "yellow")
            pedPhase = "us5Stop5"
        else:
            set_pl("green")
            pedPhase = "us5Active"
        pedTimer = now
    elif pedPhase == "us5Stop5" and (now - pedTimer) >= 3:
        set_tl(5, tl5Red, tl5Yellow, tl5Green, "red")
        set_pl("green")
        pedPhase = "us5Active"
    elif pedPhase == "us5Active" and not config.state["us5"]["detected"]:
        set_pl("flash")
        pedPhase = "us5PlFlash"
        pedTimer = now
    elif pedPhase == "us5PlFlash" and (now - pedTimer) >= 2:
        set_pl("red")
        set_tl(4, tl4Red, tl4Yellow, tl4Green, "green")
        pedPhase = None
        cyclePhase = "tl4Green"
        cycleTimer = now


def update(now):
    global pedPhase, pedTimer, pbPrinted
    if config.state["us5"]["detected"] and pedPhase is None:
        if config.state["tl4"]["colour"] != "red":
            set_tl(4, tl4Red, tl4Yellow, tl4Green, "yellow")
            pedPhase = "us5Stop4"
        elif config.state["tl5"]["colour"] != "red":
            set_tl(5, tl5Red, tl5Yellow, tl5Green, "yellow")
            pedPhase = "us5Stop5"
        else:
            set_pl("green")
            pedPhase = "us5Active"
        pedTimer = now

    pb = poll(pb1)[0] or poll(pb2)[0]
    if pb and pedPhase is None and (now - lastPedTime) >= 30:
        if not pbPrinted:
            print(f"[INFO] Pedestrian button pressed at {time.strftime('%X %x')}")
            pbPrinted = True
        pedPhase = "pedWait"
        pedTimer = now


def run_ss2():
    now = time.time()
    update(now)
    if pedPhase is not None and pedPhase.startswith("us5"):
        sequence_us5(now)
    elif pedPhase is not None:
        sequence_ped(now)
    else:
        cycle_tl(now)
    process_shift_register(config.state)


def main():
    try:
        output.output_init()
        init()
        while True:
            run_ss2()
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()