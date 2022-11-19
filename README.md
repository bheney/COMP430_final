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

## lng_lib Library
### class Lightning
#### Instance Methods
```  
__init__(mosi, miso, clk, cs, rate, interrupt)
  """
  Initialize an instance of an AS3935 lightning detector
  :param mosi: int, MOSI pin
  :param miso: int, MISO pin
  :param clk: int, CLK (clock) pin
  :param cs: int, CS (chip select) pin
  :param rate: int, Bit rate (Hz). Cannot be 500kHz
  :param interrupt: int IRQ (interrupt) pin
  """
```
* Initialize a nested object into `self.spi` with `pispi.Spi(mosi, miso, clk, cs)`
* Set the `spi.bit_rate = rate` class variable
* Set `interrupt` as in instance variable 
* Initialize the IQR pin as an input
```    
get(address)
  """
  Read a register
  :param address: int, Register address
  :return: int, the byte stored in the `address` register
  """
```
* To start the read protocol, the first two bits of the MOSI signal are always '01'        # Read the data from a given address
* Overwrite '01' to bits [7:6] of the register address
* Use `spi.read` to get the register state.
* Return the byte in the register as an int
```
send(address, data)
  """
  Write to a register
  :param address: int, register address
  :param data: int, byte to write
  :return: 
  """
```
* First two bits of the write protocol are always '00'.
* Overwrite '00' to bits [7:6] of the register address 
* Use `spi.write` to write the data
```
write_mask(address, mask, data)
  """
  Write to a portion of a register without overwriting adjacent bits
  :param address: int, Register address
  :param mask: int, Mask of register bits.
  '1's will be preserved. '0's will be overwritten
  :param data: int, byte to write
  :return: 
  """
```
* Use `get()` to read what is in the register
* Mask the data packet to '0' for insignificant bits
* Overwrite register contents with significant data
* Use `send()` to write the masked data to the register
```
in_out(indoor)
  """
  Set the chip to indoor or outdoor mode.
  Indoor mode has a drastically lower noise floor.
  :param indoor: bool, True for indoor use, False for outdoor
  :return: 
  """
```
* Set the mask 0xC1 to write bits [5:1]
* Write 0x024 for indoor mode and 0x1C for outdoor
* Use write_mask() to set register 0x00
```
power(power_mode)
  """
  Sends the chip into or returns it from power-down mode
  :param power_mode: bool, True powers the chip on. False powers it down.
  :return: 
  """
```
* Use the mask 0xFE to write bit [0]
* Write 0x00 for Power On and 0x01 for Power Off
* Use `write_mask()` to set register 0x00
```
noise_floor(level)
  """
  Sets the maximum tolerable value for signal noise without a fault.
  Lower values are prone to triggering noise faults.
  Higher values reduce sensitivity.
  :param level: int, from 0-7
  :return: 
  """
```
* Compress any out-of-range inputs to be 0-7, inclusive
* Use make 0x8F to write bits [6:4]
* Shift `level << 4` so the value is under the mask
* Use `write_mask()` to write to register 0x01
```
watchdog_sensitivity(level)
  """
  Sets the weakest signal that will trigger an event.
  Lower values are more prone to false positives.
  Higher values are less sensitive.
  :param level: int, from 0-15
  :return: 
  """
```
* Compress any out-of-range inputs to be 0-15, inclusive
* Use make 0xF0 to write bits [3:0]
* Use `write_mask()` to write to register 0x01
```
clear_stats()
    """
    Clear all stored lightning data
    Toggle 0x02[6] high-low-high
    :return: 
    """
```
* Use mask 0xBF to write bit [6]       adr = 0x02
* Use `write_mask()` to write 0x02[6] high
* Sleep 2 msec
* Use `write_mask()` to write 0x02[6] low
* Sleep 2 msec
* Use `write_mask()` to write 0x02[6] high
```       
min_strikes(level)
    """
    Sets a minimum number of strikes/15 min to trigger an interrupt
    Input   Stikes/15 min
    0       1
    1       5
    2       9
    3       16
    :param level: int, from 0-3
    :return: 
    """
```
* Compress any out-of-range inputs to be 0-3, inclusive
* Use make 0xCF to write bits [5:4]
* Shift `level << 4` so the value is under the mask
* Use `write_mask()` to write to register 0x02
```
spike_rej(level)
    """
    Sets level for how closely a signal must match "ideal" strike signature.
    Lower levels are more likely to classify disturbers as strikes
    Higher levels are more likely to classify strikes as disturbers
    :param level: int, from 0-15
    :return: 
    """
```
* Compress any out-of-range inputs to be 0-15, inclusive
* Use make 0xF0 to write bits [4:0]
* Use `write_mask()` to write to register 0x02
```
div_ratio(level)
    """
    Sets the internal factor for antenna tuning
    Factor = 16 * (<level> + 1)
    :param level: int, from 0 to 3
    :return: 
    """
```
* Compress any out-of-range inputs to be 0-3, inclusive
* Use make 0x3F to write bits [7:6]
* Shift `level << 6` so the value is under the mask
* Use `write_mask()` to write to register 0x03
```
disturbers(report)
    """
    Toggles between masking and reporting disturber events
    True signals a disturber event on IRQ pin
    False does not report disturber events
    :param report: bool
    :return: 
    """
```
* Use make 0xDF to write bits [5]
* Set message to 0x00 to turn off masking. Set to 0x20 to turn on masking.
* Use `write_mask()` to write to register 0x03
```
cap_set(level)
    """
    Sets internal capacitors to tune the antenna.
    There is no need to do this manually.
    It is called in the `calibrate()` method.
    :param level: int, 0 to 16
    :return: 
    """
```
* Compress any out-of-range inputs to be 0-16, inclusive
* Use mask 0xF0 to write bits [3:0]
* Use `write_mask()` to write to register 0x08       if level <= 0:
 ```
ant_tune()
    """
    Automatically tune the internal antenna
    This function does not currently work and I need a scope to figure 
    out why
    :return: bool, True if successful, False on failure
    """
```
* Before measuring the antenna frequency, measure the CPU speed
  * The goal is to set the lowest Div Factor for the highest accuracy
  * Too low of a Div Factor, and the CPU will not be able to read the antenna frequency
* CPU Measurement
  * Set a counter `count = 0`
  * Use dummy variable `test_var` to stand in for logic tests
  * Get the `start_time` with `time.time()`
  * While `count` < 500000:
    * Read the state of IRQ
    * Check `test var` to mimic the actual measurement loop
    * `count += 1`
    * Record `last_state = state`
  * Get the `end_time` with `time.time()`
    * `cpu_speed = count / (end_time - start_time)`
    * CPU speed must exceed (2 * 500 kHz)/(Div Factor)
  * Find the lowest Div Factor that will work 
    * Return False if CPU is not fast enough to work with the largest available scaling factor
* Set the Div Factor with `div_ratio()`
* Live Measurement
  * Start a `best_frequency` and `best_cap` tracker
  * For every capacitor level
    * Set `count = 0`
    * Set `count_to = 500000 / ((div_factor + 1) * 16)`
    * Set `last_state = 0`
    * Get `start_time`  with `time.time()`
    * Use `self.write_mask(0x08, 0x7F, 0x64)` to show the frequency on the IRQ pin
    * While count <= count_to:
      * Read IRQ
      * When IRQ changes to HIGH
        * `count += 1`
      * Record IRQ state to detect changes
    * Get `end_time` with `time.time()`
    * Use `self.write_mask(0x08, 0x7F, 0x00)` to end the frequency display on IRQ
    * `frequency = count * div_factor / (end_time - start_time)`
    * If this capacitor yielded the closest frequency to 500kHz, save it and the result to `best_frequency` and `best_cap`
* Set the best capacitor with `self.cap_set(best_cap)`
* Return True if successful
```
calibrate()
    """
    Automatic calibration of all configurable components
    :return: bool, True if successful, False on failed calibration
    """
```    
* Tune the antenna with `ant_tune()`. Return False on failure.
* Send Direct command CALIB_RCO
* Modify REG0x08[6] = 1
* Wait 2ms
* Modify REG0x08[6] = 0
* Read `trco` from 0x3A
* Read `srco` from 0x3B
* Mask over `trco` and `srco` to get bits [7:6]
* If `trco == 0x80` and `srco == 0x80`
  * Calibration was succesful
  * Retun True
  * Else, return False to indicate failure.