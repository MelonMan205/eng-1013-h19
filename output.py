#todo, create output file deterimining if write to digital  or write to shift register


from config import *
from shift_register import *
def output_init():
    init(state)
    
def write(pin, value):
    if integration:
        state[f'q{pin}'] = value
    elif not integration:
        board.digital_write(pin, value)
    