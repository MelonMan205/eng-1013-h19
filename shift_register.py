# shift_register.py
# Shift register driver for chained 74HC595s
# handles clocking bits out and latching to outputs via rclk
# Created By: Shreeneel Tarale
# Created Date: 14/05/2026
# version: v2

#store shift register array, index corresponds to qpin, 8 outputs
from config import ser, srclk, rclk, board, integration

chain_number = 4

# shift_register = [0]*8*chain_number
def init(state):
    for i in range(0, 8*chain_number):
        state[f'q{i}'] = 0

#mapping each output
def clock(bit):
    board.digital_write(ser, bit)
    board.digital_write(srclk, 1)
    board.digital_write(srclk, 0)

#push outputs
def push():
    board.digital_write(rclk, 1)
    board.digital_write(rclk, 0)

#send a input array
def send(input):
    for i in range(len(input)-1, -1, -1):
        clock(input[i])
    push()

#assemble the output array
def assemble(state):
    out = []
    for i in range(0, 8*chain_number):
        out.append(state[f'q{i}'])
    return out

#process the creation and sending of outputs
def process_shift_register(state):
    if integration:
        out = assemble(state)
        send(out)

    
    
