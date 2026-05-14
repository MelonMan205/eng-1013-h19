# output.py
# Abstraction layer for pin writes
# routes writes to digital or shift register depending on integration flag
# Created By: Shreeneel Tarale
# Created Date: 14/05/2026
# versionL v2

from config import *
import config
from shift_register import *

#initialise state
def output_init():
    init(state)
    

#do a condintional write
def write(pin, value):
    if integration:
        state[f'q{pin}'] = value
    elif not integration:
        config.board.digital_write(pin, value)
    