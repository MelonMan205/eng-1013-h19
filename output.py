#todo, create output file deterimining if write to digital  or write to shift register


from config import *


def write(pin, value):
    if integration:
        board.digital_write(pin, value)
    elif not integration:
        