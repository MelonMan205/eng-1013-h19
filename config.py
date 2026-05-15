import time 
from pymata4 import pymata4


ser = 2
srclk = 3
rclk = 4

global board
board = pymata4.Pymata4() #circuit.Arduino()
startTime = time.time()
    
integration = False

pollingRate = 0.05
sensorMountHeight = 4.5
overheightLimit = 4.0

global powerLoss
powerLoss = False

#no. of shift registers
chain_number = 4

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
    "pa1": {"sound": False},

    # warning lights
    "wl2": {"mode": "reset"}

    
    

}

