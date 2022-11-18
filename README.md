# Receiving Station
## pispi SPI Library
The pispi Python module facilitates SPI communication by directly manipulating GPIO pins on a Raspberry Pi.
### End-use functions and methods
#### Class Spi
##### Class Variables
* `bit_rate`
  * Default 10000 Hz
  * Expecting int
* `bitsec`
  * Default 1 / `bit_rate`
  * Expecting float
##### Instance Methods
```
def __init__(initmosi, initmiso, initclk, initcs):
    """
    Creates an anstance of an SPI chip
    :param initmosi: int, MOSI pin
    :param initmiso: int, MISO pin
    :param initclk: int, CLK (clock) pin
    :param initcs: int, CS (chip select) pin
    """
```
* All input parameters are set as instance variables:
    * `self.mosi = initmosi`
    * `self.miso = initmiso`
    * `self.clk = initclk`
    * `self.cs = initcs`
* Establish BCM pin numbering
* Set all specified pins for input or output
* Start CS high
```
write(write_bytes):
  """
  One-way communication via SPI
  :param write_bytes: list of ints
  :return:
  """
```
* Pass `write_bytes` to the `message()` method
* Set MOSI low
* Set CS High
```
read(address, length)
    """
    Two-way communication via SPI
    :param address: int, Register address or read protocol for
    chip
    :param length: int, length of expected response
    :return:
    """
```
* Send out the address or chip read protocol with the `message()` method
* Create empty string `read_val`
* Loop through `range(length)`:
  * Set CLK high
  * Sleep 1/2 period
  * Set CLK low
  * Sleep 1/4 period
  * Read the MISO pin. Add the value to `read_val`
  * Sleep 1/4 period
* Set MOSI low
* Set CS high
* Return `read_val` formatted as int
### Intermediate functions and methods
```
high(pin)
    """
    Sets a GPIO pin high
    :param pin: int
    :return:
    """
```
* Rename `GPIO.output(pin, GPIO.HIGH)` to improve semantics
```
low(pin)
    """
    Sets a GPIO pin low
    :param pin: int
    :return:
    """
```
* Rename `GPIO.output(pin, GPIO.LOW)` to improve semantics
```
SPI.message(message_bytes)
  """
  Intermediate method for sending a message. Not useful for top-level
  communication
  :param message_bytes: list of ints, the message to be sent
  :return:
  """
```
* Convert each item from `message_bytes` to a binary string
  * Each string has at least 8 bits. Leading '0's are added to numbers < 0x80 
* Concatenate all strings into a message
* Set CS low
* Wait 1 period
* For each bit in the message
  * Set CLK high
  * Wait 1/4 period
  * Set MOSI
  * Wait 1/4 period
  * Set CLK low
  * Wait 1/2 period
