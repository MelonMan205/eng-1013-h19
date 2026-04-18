import time 
from pymata4 import pymata4
import circuit as circuit

board = circuit.Arduino()
startTime = time.time()
    

pollingRate = 1
sensorMountHeight = 5.0
overheightLimit = 4.0

state = {
    #ultrasonic sensors
    "us1": {"detected": False, "timeOfLast": None, "triggered": False},
    "us2": {"detected": False, "timeOfLast": None, "triggered": False},
    "us3": {"detected": False, "timeOfLast": None, "triggered": False},
    "us4": {"detected": False, "timeOfLast": None, "triggered": False},
    "us5": {"detected": False, "timeOfLast": None, "triggered": False},

    #traffic lights
    "tl1": {"colour": "green"},
    "tl2": {"colour": "green"},
    "tl3": {"colour": "green"},
    "tl4": {"colour": "green"},
    "tl5": {"colour": "green"},
    "tl6": {"colour": "green"},
    "tl7": {"colour": "green"},
    
    #buzzer
    "pa1": {"sound": False}
}

