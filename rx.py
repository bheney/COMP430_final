"""
Receiver for a smart weather station
Ben Heney
COMP 430 Final Project, Fall 2022
UNH Manchester
"""

import lng_lib
lng = lng_lib.Lightning(10,9,11,24,10000,25)

#print(lng.get(0x00))
lng.in_out(False)
print(lng.get(0x00))
lng.in_out(True)
print(lng.get(0x00))
#lng.write_mask(0x01,0x45,0x22)
