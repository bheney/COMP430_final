"""
Python library for AS3935 Lightning Detector
Ben Heney
COMP 430 Final Project, Fall 2022
UNH Manchester

Based 0n Sparkfun's SPI tutorial:
https://learn.sparkfun.com/tutorials/raspberry-pi-spi-and-i2c-tutorial/all
"""
import pispi
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)


class Lightning:
    def __init__(self, mosi, miso, clk, cs, rate, interrupt):
        self.spi = pispi.Spi(mosi, miso, clk, cs)
        self.spi.bit_rate = rate
        self.int = interrupt

    def get(self, address):
        # Read the data from a given address
        # First two bits of read signal are always "01"
        # Next six bits are the address
        print('lng getting address {}'.format(address))
        byte = 0x40  # 0b01000000
        byte = byte | address  # Combines the read signal & address
        print('lng requesting address from {}'.format(byte))
        return self.spi.read([byte], 8)

    def send(self, address, data):
        # Write data to a register using bitwise logic
        # First two bits are always "00"
        # Next six bits are the address
        # Next eight bits are the data
        mask = 0X00  # 0b11000000
        address = mask ^ address
        print('lng writing to {}, sending {}'.format(address, data))
        self.spi.write([address, data])

    def write_mask(self, address, mask, data):
        # Read the data at an address
        # Apply a mask to change all write bits to 0
        # Mask needs to be '1' for non-write bits and '0' for write bits
        # Write to those bits
        byte = self.get(address)  # Get what's there
        byte = byte & mask  # Write 0s to write bits. Keep others the same
        data = data & ~mask
        byte = byte | data  # Write the new data to the writeable bits
        self.send(address, byte)

    def in_out(self, indoor: bool):
        # True for indoor use
        # False for outdoor use
        mask = 0xC1  # 11000001
        if indoor:
            mode = 0x24  # 00100100
        else:
            mode = 0x1C  # 00011100
        self.write_mask(0x00, mask, mode)

    def power(self, power_mode: bool):
        # True for power on
        # False for power down
        mask = 0xFE  # 1111110
        if power_mode:
            mode = 0x00  # 00000000
        else:
            mode = 0x01  # 00000001
        self.write_mask(0x00, mask, mode)

    def noise_floor(self, level: int):
        # Expecting an integer 0-7
        # Lower numbers are more prone to triggering a noise fault
        # Higher numbers reduce sensitivity
        # This filters out constant interference

        if level < 0:
            level = 0
        if level > 7:
            level = 7
        mask = 0x8F  # 10001111
        level = level << 4
        self.write_mask(0x01, mask, level)

    def watchdog_sensitivity(self, level: int):
        # Expecting an integer 0-15
        # Lower numbers are more prone to false positives
        # Higher numbers are less sensitive
        # This is the weakest signal that will trigger an event

        if level < 0:
            level = 0
        if level > 15:
            level = 15
        mask = 0x8F  # 11110000
        self.write_mask(0x01, mask, level)

    def clear_stats(self):
        # Clear all stored lightning data
        # Toggle 0x02[6] high-low-high
        adr = 0x02
        mask = 0xBF  # 10111111
        self.write_mask(adr, mask, 0x40)
        time.sleep(.002)
        self.write_mask(adr, mask, 0x00)
        time.sleep(.002)
        self.write_mask(adr, mask, 0x40)

    def min_strikes(self, level: int):
        # Requires a minimum number of strikes in 15 min before interrupt
        # Levels are 1, 5, 9, 16
        # Expecting int 0-3
        if level < 0:
            level = 0
        if level > 3:
            level = 3
        level = level << 4
        mask = 0xCF  # 11001111
        self.write_mask(0x02, mask, level)

    def spike_rej(self, level: int):
        # Expecting an integer 0-15
        # Lower numbers are more prone to false positives
        # Higher numbers are less sensitive
        # This is how closely the signal resembles lightning

        if level < 0:
            level = 0
        if level > 15:
            level = 15
        mask = 0x8F  # 11110000
        self.write_mask(0x02, mask, level)

    def div_ratio(self, level: int):
        # A factor used in antenna tuning
        # Factor used in IC algorithm is 16*(level+1)
        if level < 0:
            level = 0
        if level > 3:
            level = 3
        level = level << 6
        mask = 0xCF  # 00111111
        self.write_mask(0x03, mask, level)

    def disturbers(self, report: bool):
        # Interrupts and reports out disturbers if true
        # Does not interrupt or report disturbers if false
        mask = 0xDF  # 11011111
        if report:
            byte = 0x00
        else:
            byte = 0x20  # 00100000
        self.write_mask(0x03, mask, byte)

    def calibrate(self):
        # Send Direct command CALIB_RCO
        # Modify REG0x08[6] = 1
        # Wait 2ms
        # Modify REG0x08[6] = 0
        self.send(0x3D, 0x96)
        self.write_mask(0x08, 0xBF, 0x40)
        time.sleep(.002)
        self.write_mask(0x08, 0xBF, 0x00)
        time.sleep(.002)
        trco = self.get(0x3A)
        srco = self.get(0x3B)
        if trco == 0x80 and srco == 0x80:
            return True
        else:
            return False

    def ant_trim(self):
        count = 0
        state = False
        self.write_mask(0x08, 0x7F, 0x64)
