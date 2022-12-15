"""
Receiver for a smart weather station
Ben Heney
COMP 430 Final Project, Fall 2022
UNH Manchester
"""
import radio
import RPi.GPIO as GPIO
import time

mosi=16
miso=17
clk=13
cs=12
ce=6
irq=5

rx=radio.Radio(mosi, miso, clk, cs, ce, irq, address_width=5,frequency=76,air_data_rate=1,crc=2)
# rx.disable_pipe(0)
# rx.enable_pipe(1, "2Node", auto_ack=True, dynamic=False,
#                    payload_len=16)
rx.setup_hack()

registers=[r for r in range (0x0C)]
registers.append(0x1C)
registers.append(0x1D)
for register in registers:
    if register==0x0A or register==0x0b:
        buffer=5
    else:
        buffer=1
    print(f'Register {hex(register)}: {hex(rx.get(register,buffer))}')

while True:
    print(message=rx.listen())

    