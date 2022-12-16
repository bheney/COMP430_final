"""
Python library for AS3935 Lightning Detector
Ben Heney
COMP 430 Final Project, Fall 2022
UNH Manchester
"""
import pispi
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)


class Lightning:
    def __init__(self, mosi, miso, clk, cs, interrupt):
        """
        Initialize an instance of an AS3935 lightning detector
        :param mosi: int, MOSI pin
        :param miso: int, MISO pin
        :param clk: int, CLK (clock) pin
        :param cs: int, CS (chip select) pin
        :param interrupt: int IRQ (interrupt) pin
        """
        self.spi = pispi.Spi(mosi, miso, clk, cs, False)
        self.spi.bit_rate = 10000
        self.int = interrupt
        GPIO.setup(self.int, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get(self, address):
        """
        Read a register
        :param address: int, Register address
        :return: int, the byte stored in the `address` register
        """
        # Read the data from a given address
        # First two bits of read signal are always "01"
        # Next six bits are the address
        # print('lng getting address {}'.format(address))
        address = address & 0b00111111
        outgoing = 0b01000000 | address
        # print('lng requesting address from {}'.format(byte))
        incoming = self.spi.transaction([outgoing], 1)
        incoming = incoming[8:]
        return int(incoming, 2)

    def send(self, address, data):
        """
        Write to a register
        :param address: int, register address
        :param data: int, byte to write
        :return:
        """
        # Write data to a register using bitwise logic
        # First two bits are always "00"
        # Next six bits are the address
        # Next eight bits are the data
        address = 0b00111111 & address
        # print('lng writing to {}, sending {}'.format(address, data))
        self.spi.transaction([address, data])

    def write_mask(self, address, mask, data):
        """
        Write to a portion of a register without overwriting adjacent bits
        :param address: int, Register address
        :param mask: int, Mask of register bits.
        '1's will be preserved. '0's will be overwritten
        :param data: int, byte to write
        :return:
        """
        # Read the data at an address
        # Apply a mask to change all write bits to 0
        # Mask needs to be '1' for non-write bits and '0' for write bits
        # Write to those bits
        byte = self.get(address)  # Get what's there
        byte = byte & mask  # Write 0s to write bits. Keep others the same
        data = data & ~mask  # Write 0s to the persistent bits of `data`
        byte = byte | data  # Combine the packets
        self.send(address, byte)

    def in_out(self, indoor: bool):
        """
        Set the chip to indoor or outdoor mode.
        Indoor mode has a drastically lower noise floor.
        :param indoor: bool, True for indoor use, False for outdoor
        :return:
        """
        mask = 0b11000001
        if indoor:
            mode = 0b00100100
        else:
            mode = 0b00011100
        self.write_mask(0x00, mask, mode)
        print('Indoor/Outdoor set')

    def power(self, power_mode: bool):
        """
        Sends the chip into or returns it from power-down mode
        :param power_mode: bool, True powers the chip on. False powers it down.
        :return:
        """
        mask = 0xFE  # 1111110
        if power_mode:
            mode = 0x00  # 00000000
        else:
            mode = 0x01  # 00000001
        self.write_mask(0x00, mask, mode)

    def noise_floor(self, level: int):
        """
        Sets the maximum tolerable value for signal noise without a fault.
        Lower values are prone to triggering noise faults.
        Higher values reduce sensitivity.
        :param level: int, from 0-7
        :return:
        """
        if level < 0:
            level = 0
        if level > 7:
            level = 7
        mask = 0b10001111
        level = level << 4
        self.write_mask(0x01, mask, level)
        print('Noise Floor set')

    def watchdog_sensitivity(self, level: int):
        """
        Sets the weakest signal that will trigger an event.
        Lower values are more prone to false positives.
        Higher values are less sensitive.
        :param level: int, from 0-15
        :return:
        """
        if level < 0:
            level = 0
        if level > 15:
            level = 15
        mask = 0b11110000
        self.write_mask(0x01, mask, level)
        print('Watchdog Sensitivity set')

    def clear_stats(self):
        """
        Clear all stored lightning data
        Toggle 0x02[6] high-low-high
        :return:
        """
        adr = 0x02
        mask = 0b10111111
        self.write_mask(adr, mask, 0x40)
        time.sleep(.002)
        self.write_mask(adr, mask, 0x00)
        time.sleep(.002)
        self.write_mask(adr, mask, 0x40)
        print('Stats cleared')

    def min_strikes(self, level: int):
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
        if level < 0:
            level = 0
        if level > 3:
            level = 3
        level = level << 4
        mask = 0b11001111
        self.write_mask(0x02, mask, level)

    def spike_rej(self, level: int):
        """
        Sets level for how closely a signal must match "ideal" strike signature.
        Lower levels are more likely to classify disturbers as strikes
        Higher levels are more likely to classify strikes as disturbers
        :param level: int, from 0-15
        :return:
        """
        if level < 0:
            level = 0
        if level > 15:
            level = 15
        mask = 0b11110000
        self.write_mask(0x02, mask, level)

    def div_ratio(self, level: int):
        """
        Sets the internal factor for antenna tuning
        Factor = 16 * (<level> + 1)
        :param level: int, from 0 to 3
        :return:
        """
        if level < 0:
            level = 0
        if level > 3:
            level = 3
        level = level << 6
        mask = 0b00111111
        self.write_mask(0x03, mask, level)
        print('Div Ratio set to {}'.format(level))

    def disturbers(self, report: bool):
        """
        Toggles between masking and reporting disturber events
        True signals a disturber event on IRQ pin
        False does not report disturber events
        :param report: bool
        :return:
        """
        mask = 0b11011111
        if report:
            byte = 0x00
        else:
            byte = 0b00100000
        self.write_mask(0x03, mask, byte)

    def cap_set(self, level):
        """
        Sets internal capacitors to tune the antenna.
        There is no need to do this manually.
        It is called in the `calibrate()` method.
        :param level: int, 0 to 16
        :return:
        """
        if level <= 0:
            level = 0
        elif level >= 16:
            level = 16
        else:
            level = int(level)
        self.write_mask(0x08, 0xF0, level)
        print('Capacitors set to {}'.format(level))

    def ant_tune(self):
        """
        Automatically tune the internal antenna
        This function does not currently work and I need a scope to figure
        out why
        :return: bool, True if successful, False on failure
        """
        count = 0
        test_var = True
        start_time = time.time()
        while count < 500000:
            state = GPIO.input(self.int)
            if test_var == True and test_var == True:
                count += 1
            last_state = state
        end_time = time.time()
        cpu_speed = count / (end_time - start_time)
        print('CPU Speed is {} Hz'.format(cpu_speed))
        # CPU speed must exceed (2 * 500 kHz)/(internal scaling factor)
        div_bool = False
        target_speed = 5e5 * 2 * 2
        # 500 kHz * 2 (to read high and low in 1 cycle) *2 (safety)
        for scale in range(4):
            div_ratio = (scale + 1) * 16
            if target_speed / div_ratio < cpu_speed:
                div_factor = scale
                div_bool = True
                break
        if div_bool:
            print('Div Ratio is {}; Div Factor is {}'.format(div_ratio,
                                                             div_factor))
        else:
            print('Setting Div Factor failed.')
            return False

        # Set the calculated div and run the tuning process
        self.div_ratio(div_factor)
        # self.div_ratio(3)
        # Live measurement
        best_frequency = 0
        best_cap = 16
        for cap in range(16):
            count = 0
            count_to = 500000 / ((div_factor + 1) * 16)
            last_state = 0
            print('Begin capacitor analysis')
            start_time = time.time()
            self.write_mask(0x08, 0x7F, 0x64)
            while count <= count_to:
                state = GPIO.input(self.int)
                # print (state)
                if last_state == 0 and state == 1:
                    count += 1
                last_state = state
                print(count)
            end_time = time.time()
            self.write_mask(0x08, 0x7F, 0x00)
            frequency = count * div_factor / (end_time - start_time)
            print('Capacitor {} yielded {} Hz'.format(cap, frequency))
            if abs(frequency - 500000) < abs(best_frequency - 500000):
                best_frequency = frequency
                best_cap = cap
        self.cap_set(best_cap)
        print('Antenna tuned')
        return True

    def calibrate(self):
        """
        Automatic calibration of all configurable components
        :return: bool, True if successful, False on failed calibration
        """
        # Tune the antenna
        # Need a scope to see what's going on. Not registering changes on IRQ
        """if self.ant_tune():
            pass
        else:
            print ('Antenna Failed to tune.')
            return False"""
        # Send Direct command CALIB_RCO
        # Modify REG0x08[6] = 1
        # Wait 2ms
        # Modify REG0x08[6] = 0
        self.send(0x3D, 0x96)
        time.sleep(.002)
        self.write_mask(0x08, 0xBF, 0x40)
        time.sleep(.002)
        self.write_mask(0x08, 0xBF, 0x00)
        time.sleep(.002)
        trco = self.get(0x3A)
        srco = self.get(0x3B)
        # print ('TRCO reads {}, SRCO reads {}'.format(trco, srco))
        trco = trco & 0xC0
        srco = srco & 0xC0
        # print ('TRCO yields {}, SRCO yields {}'.format(trco, srco))
        if trco == 0x80 and srco == 0x80:
            print('TRCO and SRCO successfully calibrated')
            return True
        else:
            print('TRCO/SRCO calibration failed.')
            return False
