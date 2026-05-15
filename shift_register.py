# shift_register.py
# Shift register driver for chained 74HC595s
# Handles clocking bits out and latching to outputs via rclk
# Created By: Shreeneel Tarale
# Created Date: 14/05/2026
# version: v2

from config import ser, srclk, rclk, board, integration, chain_number


def init(state):
    """
    Initialises all shift register output slots in the state dict to 0.

    Parameters:
        state (dict): the shared config state dict to initialise

    Returns:
        None
    """
    for i in range(0, 8 * chain_number):
        state[f'q{i}'] = 0


def clock(bit):
    """
    Clocks a single bit into the shift register by pulsing the shift clock.

    Parameters:
        bit (int): the bit value to clock in, 0 or 1

    Returns:
        None
    """
    board.digital_write(ser, bit)
    board.digital_write(srclk, 1)
    board.digital_write(srclk, 0)


def push():
    """
    Latches the current shift register contents to the outputs by pulsing rclk.

    Parameters:
        None

    Returns:
        None
    """
    board.digital_write(rclk, 1)
    board.digital_write(rclk, 0)


def send(bitArray):
    """
    Clocks out every bit in bitArray MSB-last then latches the outputs.

    Parameters:
        bitArray (list): list of int bit values to send to the shift register

    Returns:
        None
    """
    for i in range(len(bitArray) - 1, -1, -1):
        clock(bitArray[i])
    push()


def assemble(state):
    """
    Builds the output bit array from the state dict q-pin entries.

    Parameters:
        state (dict): the shared config state dict containing q0..qN values

    Returns:
        list: ordered list of bit values ready to pass to send()
    """
    out = []
    for i in range(0, 8 * chain_number):
        out.append(state[f'q{i}'])
    return out


def process_shift_register(state):
    """
    Assembles the current state into a bit array and sends it to the shift
    register chain. Only runs when integration mode is active.

    Parameters:
        state (dict): the shared config state dict

    Returns:
        None
    """
    if integration:
        out = assemble(state)
        send(out)