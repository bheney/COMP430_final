"""
Receiver for a smart weather station
Ben Heney
COMP 430 Final Project, Fall 2022
UNH Manchester
"""

import lng_lib
import RPi.GPIO as GPIO
import time

mosi = 10
miso = 9
clk = 11
cs = 26
irq = 27

lng = lng_lib.Lightning(mosi, miso, clk, cs, irq)
lng.in_out(True)
lng.noise_floor(3)
lng.watchdog_sensitivity(11)
lng.min_strikes(0)
lng.spike_rej(11)
lng.disturbers(True)
if lng.calibrate():
    pass
else:
    raise Exception('Calibration Failed')
while True:
    if GPIO.input(lng.int) == 1:
        int_type = lng.get(0x03)
        int_type = int_type & 0x0F
        if int_type == 0x01:
            event = 'noise'
        elif int_type == 0x04:
            event = 'disturber'
        elif int_type == 0x08:
            event = 'lightning'
        else:
            event = 'undefined'
        print('{} detected'.format(event))
        now = time.gmtime()
        time_write = '{}-{}-{} {}:{}:{}'.format(now[2], now[1], now[0], now[3],
                                                now[4], now[5])
        distance = lng.get(0x07)
        distance = distance & 0x3F
        lng_log = open('lng_log.csv', 'r')
        log_mem = lng_log.read()
        lng_log.close()
        lng_log = open('lng_log.csv', 'w')
        lng_log.write(
            '{}\n{},{},{}'.format(log_mem, time_write, event, distance))
        lng_log.close()
