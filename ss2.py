from pymata4 import pymata4
import time
board = pymata4.Pymata4()

#inputs
board.set_pin_mode_digital_input(2) #push button 1
board.set_pin_mode_digital_input(3) #push button 2

#outputs
board.set_pin_mode_digital_output(4) #TL4 green
board.set_pin_mode_digital_output(5) #TL4 yellow
board.set_pin_mode_digital_output(6) #TL4 red
board.set_pin_mode_digital_output(7) #TL5 green
board.set_pin_mode_digital_output(8) #TL5 yellow
board.set_pin_mode_digital_output(9) #TL5 red
board.set_pin_mode_digital_output(10) #PL1 green
board.set_pin_mode_digital_output(11) #PL1 red 
board.set_pin_mode_digital_output(12) #PL2 green
board.set_pin_mode_digital_output(13) #PL2 red

def R1_1():
            
            board.digital_write(5,1) #TL4 yellow on 
            board.digital_write(6,0) #TL4 red off
            board.digital_write(4,0) #TL4 green off
            time.sleep(3)
            board.digital_write(6,1) #TL4 red on
            board.digital_write(5,0) #TL4 yellow off
            board.digital_write(10,1)
            board.digital_write(12,1)
            time.sleep(3)
            for i in range(5):   # repeat ~2 seconds
                board.digital_write(10, 0)
                board.digital_write(12, 0)
                time.sleep(0.2)
                board.digital_write(10, 1)
                board.digital_write(12, 1)
                time.sleep(0.2)
                

            
def R1_2():
            board.digital_write(7,0)
            board.digital_write(8,1)
            board.digital_write(9,0)
            time.sleep(3)
            board.digital_write(8,0)
            board.digital_write(9,1)
            board.digital_write(10,1)
            board.digital_write(12,1)
            time.sleep(3)
            for i in range(5):   # repeat ~2 seconds
                board.digital_write(10, 0)
                board.digital_write(12, 0)
                time.sleep(0.2)
                board.digital_write(10, 1)
                board.digital_write(12, 1)
                time.sleep(0.2)
            



def R3():

    while True:
        board.digital_write(4,1)
        board.digital_write(9,1)
        board.digital_write(6,0)
        board.digital_write(8,0)
        board.digital_write(10, 0)
        board.digital_write(12, 0)
        
        for i in range(200):  # ~20 seconds
            if board.digital_read(2)[0] == 1 or board.digital_read(3)[0] == 1:
                print("Button pressed 1")
                return "RED_ON"  # ← send signal
            time.sleep(0.1)

        board.digital_write(4,0)
        board.digital_write(5,1)
        
        for i in range(30):  # ~3 seconds
                    if board.digital_read(2)[0] == 1 or board.digital_read(3)[0] == 1:
                        print("Button pressed 2")
                        return "RED_OFF"   # ← send signal
                    time.sleep(0.1)

        board.digital_write(5,0)
        board.digital_write(6,1)
        board.digital_write(7,1)
        board.digital_write(9,0)
        
        for i in range(100):  # ~100 seconds
                    if board.digital_read(2)[0] == 1 or board.digital_read(3)[0] == 1:
                        print("Button pressed 2")
                        return "RED_OFF"   # ← send signal
                    time.sleep(0.1)
        
        board.digital_write(8,1)
        board.digital_write(7,0)
        
        for i in range(30):  # ~3 seconds
                    if board.digital_read(2)[0] == 1 or board.digital_read(3)[0] == 1:
                        print("Button pressed 2")
                        return "RED_OFF"   # ← send signal
                    time.sleep(0.1)

        
    

def program():
    while True:
        result = R3()

        if result == "RED_ON":
            R1_1()
            continue

        elif result == "RED_OFF":
            R1_2()
            continue

while True:
    try:
        program()
    except KeyboardInterrupt:
        board.shutdown()
        break


board.shutdown()