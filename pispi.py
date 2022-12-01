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
    def __init__(self, mosi: int, miso: int, clk: int, cs: int, clk_mode=True):
        """
        Creates an instance of an SPI chip
        :param mosi: int, MOSI pin
        :param miso: int, MISO pin
        :param clk: int, CLK (clock) pin
        :param cs: int, CS (chip select) pin
        :param clk_mode: bool, clk rising True/clk falling False
        """
        self.mosi = mosi
        self.miso = miso
        self.clk = clk
        self.cs = cs
        self.mode = clk_mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.miso, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.mosi, GPIO.OUT)
        GPIO.setup(self.clk, GPIO.OUT)
        GPIO.setup(self.cs, GPIO.OUT)
        high(self.cs)

    bit_rate = 10000
    bitsec = 1 / bit_rate

    def transaction(self, data, read_buffer=0):
        """
        Conduct an SPI transaction over GPIO pins
        :param data: lst, outgoing data as list of ints
        :param read_buffer: int, number of bytes to continue clock operations
            after last outgoing bit
        :return: str, MISO status for EVERY clk pulse (includes a status
        register)
        """
        # Convert data and read_buffer to a string
        mosi = ''
        for datum in data:
            if datum > 255:
                raise Exception("SPI data too large. Must be less than 255.")
            byte = bin(datum)
            byte = byte[2:]
            while len(byte) < 8:
                byte = '0' + byte
            mosi += byte
        mosi += read_buffer * 8 * '0'

        # Start the SPI signal
        low(self.cs)
        time.sleep(self.bitsec)
        miso_str: str = ''
        for bit in mosi:
            if self.mode:
                low(self.clk)
            else:
                high(self.clk)
            time.sleep(self.bitsec / 4)

            if bit == '0':
                low(self.mosi)
            elif bit == '1':
                high(self.mosi)
            time.sleep(self.bitsec / 4)

            if self.mode:
                high(self.clk)
            else:
                low(self.clk)
            time.sleep(self.bitsec / 2)

            # Read the MISO pin
            if 0 == GPIO.input(self.miso):
                miso_str += '0'
            else:
                miso_str += '1'
        high(self.cs)
        return miso_str
