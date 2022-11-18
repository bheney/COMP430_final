"""
A Python-based SPI library using RPi.GPIO and pin bashing.
Ben Heney 11-18-22
"""
import RPi.GPIO as GPIO
import time


def high(pin):
    """
    Sets a GPIO pin high
    :param pin: int
    :return:
    """
    GPIO.output(pin, GPIO.HIGH)


def low(pin):
    """
    Sets a GPIO pin low
    :param pin: int
    :return:
    """
    GPIO.output(pin, GPIO.LOW)


class Spi:
    def __init__(self, initmosi, initmiso, initclk, initcs):
        """
        Creates an anstance of an SPI chip
        :param initmosi: int, MOSI pin
        :param initmiso: int, MISO pin
        :param initclk: int, CLK (clock) pin
        :param initcs: int, CS (chip select) pin
        """
        self.mosi = initmosi
        self.miso = initmiso
        self.clk = initclk
        self.cs = initcs
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.miso, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.mosi, GPIO.OUT)
        GPIO.setup(self.clk, GPIO.OUT)
        GPIO.setup(self.cs, GPIO.OUT)
        high(self.cs)

    bit_rate = 10000
    bitsec = 1 / bit_rate

    def message(self, message_bytes):
        """
        Intermediate method for sending a message. Not useful for top-level
        communication
        :param message_bytes: list of ints, the message to be sent
        :return:
        """
        bits = ''
        count = 0
        for byte in message_bytes:
            count += 1
            bin_bits = bin(byte)
            bin_bits = bin_bits[2:]
            while len(bin_bits) < 8:
                bin_bits = '0' + bin_bits
            bits += bin_bits
        low(self.cs)
        time.sleep(self.bitsec)
        for bit in bits:
            high(self.clk)
            time.sleep(self.bitsec / 4)
            if bit == '0':
                low(self.mosi)
            elif bit == '1':
                high(self.mosi)
            time.sleep(self.bitsec / 4)
            low(self.clk)
            time.sleep(self.bitsec / 2)

    def write(self, write_bytes):
        """
        One-way communication via SPI
        :param write_bytes: list of ints
        :return:
        """
        self.message(write_bytes)
        low(self.mosi)
        high(self.cs)

    def read(self, address, length):
        """
        Two-way communication via SPI
        :param address: int, Register address or read protocol for
        chip
        :param length: int, length of expected response
        :return:
        """
        self.message(address)
        read_val = ''
        for _ in range(length):
            high(self.clk)
            time.sleep(self.bitsec / 2)
            low(self.clk)
            time.sleep(self.bitsec / 4)
            if 0 == GPIO.input(self.miso):
                read_val += '0'
            else:
                read_val += '1'
            time.sleep(self.bitsec / 4)
        low(self.mosi)
        high(self.cs)
        return int(read_val, 2)
