# import pyfirmata

# led_pin = 7
# button_pin = 8

# arduino_addr = "/dev/cu.usbmodem14201"

# board = pyfirmata.Arduino(arduino_addr)

# # it = pyfirmata.util.Iterator(board)
# # it.start()

# board.digital[button_pin].mode = pyfirmata.INPUT

# while True:
#     is_pressed = board.digital[button_pin].read()
#     if is_pressed:
#         print("Pressed? {}".format(is_pressed))
#         board.digital[led_pin].write(1)
#     else:
#         board.digital[led_pin].write(0)

import pyfirmata

import time

board = pyfirmata.Arduino('/dev/cu.usbmodem14201')

it = pyfirmata.util.Iterator(board)
it.start()

board.digital[10].mode = pyfirmata.INPUT

while True:
    sw = board.digital[10].read()
    if sw is True:
        board.digital[13].write(1)
    else:
        board.digital[13].write(0)
    time.sleep(0.1)
