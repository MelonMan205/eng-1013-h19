# output.py
# Abstraction layer for pin writes
# Routes writes to digital or shift register depending on integration flag
# Created By: Shreeneel Tarale
# Created Date: 14/05/2026
# version: v2

from config import *
import config
from shift_register import *


def output_init():
    """
    Initialise the shift register  so all outputs  at 0

    Parameters:
        None

    Returns:
        None
    """
    init(state)


def write(pin, value):
    """
    Write a value to a pin only to the shift register when integration
    is enabled or directly to arduino digital otherwise

    Parameters:
        pin (int): the pin or shift register output index to write to
        value (int): the value to write 0 or 1

    Returns:
        None
    """
    if integration:
        state[f'q{pin}'] = value
    else:
        config.board.digital_write(pin, value)