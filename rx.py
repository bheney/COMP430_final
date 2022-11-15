"""
Receiver for a smart weather station
Ben Heney
COMP 430 Final Project, Fall 2022
UNH Manchester
"""

import lng_lib
lng = lng_lib.Lightning(10,9,11,26,10000,27)
lng.in_out(True)
lng.noise_floor(0)
lng.watchdog_sensitivity(0)
lng.min_strikes(0)
lng.spike_rej(0)
lng.disturbers(True)
