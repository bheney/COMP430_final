"""
Receiver for a smart weather station
Ben Heney
COMP 430 Final Project, Fall 2022
UNH Manchester
"""
import radio
mosi=13
miso=16
clk=17
cs=4
ce=12
irq=5

rx=radio.Radio(mosi, miso, clk, cs, ce, irq, address_width=5,frequency=76,air_data_rate=0,crc=1)
rx.enable_pipe(0, 'AAAAA', auto_ack=True, dynamic=False,
                    payload_len=4)
rx.enable_pipe(1, '1Node', auto_ack=True, dynamic=False,
                   payload_len=4)
# registers=[]
# for register in range (0x18):
#     registers.append(register)
# print('Final state')
# for register in registers:
#     print(f'Register {register} reads {bin(rx.get(register))}')
# print (f'Register 0x0A: {hex(rx.get(0x0A,5))}')
# print (f'Register 0x0B: {hex(rx.get(0x0B,5))}')
while True:
    print(message=rx.listen())