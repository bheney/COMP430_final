# RX Station
## pispi SPI Library
The pispi Python module facilitates SPI communication by directly manipulating GPIO pins on a Raspberry Pi.
### End-use functions and methods
#### Class Spi
##### Class Variables
* `bit_rate`
  * clk frequency
  * Default 10000 Hz
  * Expecting int
* `bitsec`
  * Default 1 / `bit_rate`
  * Expecting float
##### Instance Methods
```
def __init__(self, mosi: int, miso: int, clk: int, cs: int, clk_mode=True):
"""
  Creates an instance of an SPI chip
  :param mosi: int, MOSI pin
  :param miso: int, MISO pin
  :param clk: int, CLK (clock) pin
  :param cs: int, CS (chip select) pin
  :param clk_mode: bool, clk rising True/clk falling False
  """
```
* All input parameters are set as instance variables:
    * `self.mosi = mosi`
    * `self.miso = miso`
    * `self.clk = clk`
    * `self.cs = cs`
    * `self.clk_mode=clk_mode`
* Establish BCM pin numbering
* Set all specified pins for input or output
* Start CS high
```
def transaction(self, data, read_buffer=0):
"""
  Conduct an SPI transaction over GPIO pins
  :param data: lst, outgoing data as list of ints<255
  :param read_buffer: int, number of bytes to continue clock operations
      after last outgoing bit
  :return: str, MISO status for EVERY clk pulse (includes a status
  register)
  """
```
* Check that every item in `data` is <= 255
  * Method only works with byte data
* Accumulate `mosi_str` that represents `data` in binary characters
* Iterate through `mosi_str`
  * Each cycle will prepare clk
  * Set the MOSI pin
  * Signal clk
  * Read the MISO pin
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
## lng_lib Library
### class Lightning
#### Instance Methods
```  
__init__(mosi, miso, clk, cs, interrupt)
  """
  Initialize an instance of an AS3935 lightning detector
  :param mosi: int, MOSI pin
  :param miso: int, MISO pin
  :param clk: int, CLK (clock) pin
  :param cs: int, CS (chip select) pin
  :param interrupt: int IRQ (interrupt) pin
  """
```
* Initialize a nested object into `self.spi` with `pispi.Spi(mosi, miso, clk, cs, False)`
* Set the `spi.bit_rate = rate` class variable at 10000 hZ
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
* To start the read protocol, the first two bits of the MOSI signal are always '01'
* Overwrite '01' to bits [7:6] of the register address
* Use `spi.transaction` to get the register state.
* Trim out the status register, as there isn't one
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
* Use `spi.transaction` to write the data
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
* Use `get()` to read what is in the register into `byte`
* Write 0s to write bits of `byte`. Keep others the same
* Write 0s to the persistent bits of `data`
* Combine `byte` and `data`
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
  * Calibration was successful
  * Return True
  * Else, return False to indicate failure.
## radio Library
### Class Radio
```
def __init__(self, mosi, miso, clk, cs, ce, irq, address_width=5,
         frequency=76, air_data_rate=1, crc=0):
  """
  Initialize an instance of an nRF24l01 transceiver
  :param mosi: int, MOSI pin
  :param miso: int, MISO pin
  :param clk: int, CLK (clock) pin
  :param cs: int, CS (chip select) pin
  :param ce: int ce pin
  :param irq: int, interrupt pin
  :param address_width: int, length of pipe addresses
  :param frequency: int, operating frequency
  :param air_data_rate: int, over-the-air data rate
  :param irq: crc, acknowledgement encoding variable
  """
```
* Nest `pispi.Spi` into `self.spi`
* Set `spi.bit_rate = 10000` hZ
* Configure the ce and IRQ pins
* Create dictionary `self.pipe_address` and populate it with the default addresses for pipes 0 and 1
* Create dictionary `self.pipe_dynamic` and populate it with the default setting (static) for pipes 0 and 1
```
def write(self, register, *data):
  """
  Write data to a register
  :param register: int, register address
  :param data: int, data to send
  :return: int, status register
  """
```
* Mask the register address (AAAAA) with the write command: 0b001AAAAA
* Generate a list of bytes in `message` with the write command/address and all arguments from `*data`
* Send the data stream with `self.spi.transaction(message)`
* Return the status register as an int
```
def write_mask(self, register, mask, data):
  """
  Write to a portion of a register
  :param register: int, register address
  :param mask: int, mask where '0' will be modified and '1' will be held
  :param data: int, data to write
  :return: int, status register
  """
```
* Use `get()` to read the data in the register and store as `state`
* Write '0's to the write bits of `state`
* Write `0`s to the persistent bits of `data`
* Combine `state` and `data`
* Use `write` to write the modified data and return the status register

```
def get(self, address, buffer=1):
  """
  Read a register
  :param buffer: int, size of response (in bytes)
      does not include a status byte
  :param address: int, Register address
  :return: int, the byte stored in the `address` register
  """
 ```
* Send the read command to `address` register
* Return `buffer` number of bytes as an integer
  * Trim off the status register
```
  def disable_pipe(self, pipe_id):
  Disable a communicaiton pipe
  :param pipe_id: int, the pipe to be disables
  :return: 
 ```
* Disable `pipe_id` in register 0x02
```
def enable_pipe(self, pipe_id, pipe_address, auto_ack=True, dynamic=True,
                      payload_len=32):
  """
  Initialize a communicaiton pipe
  :param pipe_id: int, the pipe to be initialized
  :param pipe_address: int, the address of the pipe
  :param auto_ack: bool, True: enable auto-acknowledgements, False: 
    disable auto-acknowledgements
  :param dynamic: bool, True: enable dynamic payloads, False: disable 
    dynamic payloads
  :param payload_len: int, the length of static payloads
  :return:
  """
```
* Enable pipe in register 0x02
* Enable/Disable AutoAck in register 0x01
* Set payload width:
  * if dynamic: Enable dynamic payloads in 0x1C adn 0x1D
  * if static: Write payload length in 0x11-0x16
* Set address:
  * Written LSByte first
  * Addresses 1-5 cannot be the same as 0
  * Address cannot start with 0b10
  * Address must contain more than one level shift
  * LSB of pipe address must be unique
```
def listen(self):
  """
  Wait for incomming data and report it
  :return: str, incomming data
  """
```
* Set radio in RX mode
* Set CE high
* Wait for interrupt to go high                  print(self.spi.transaction([0xFF], 0))
* Get pipe address for incoming data
* Get the data length if dynamic
* Stop listening with CE low
* return message
```
def setup_hack(self):
  """
  Copying the register data from RF24 library on Arduino
  :return: 
  """
```
* Create dictionary `image`
  * Keys: register addresses
  * Values register values from arduino setup
  * Write all values to all keys
## lng_monitor.py
* Initialize an instance of `Lightning` class from `lng_lib`
* Set to indoor mode
* Set operating parameters
  * These will require tuning based on the environment
* Calibration feature is still not fully functional
* When an interrupt is detected:
  * Get the type and distance
  * Write that info, along with the time, into CSV `lng_log.csv`

## rx_work_around.py
###Funcitons
```
def parse_str(string, delim):
    """
    Separate the data stream from the radio
    :param string: str, the incoming data stream
    :param delim: str, the parameter to parse for
    :return: 
    """
```
* Data coming in from the radio over UART will have the format: `T<Temperature>TP<Pressure>PH<Humidity>H`
* This function returns the numeric data between the deliminators
### Main Program
* Start a UART serial connection with the Arduino
* When data arrives:
    * Use `parse_str()` to store the atmospheric data into each parameters' respective variable
    * Get the time and store it in a human-readable string
    * Store the data in 'wx_log.csv'
    * Pull the last set of measurements from `lng_log.csv` and `wx_log.csv`
    * Embed the latest data into an HTML page
    * Same the HTML page