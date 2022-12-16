import pispi
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)


class Radio:
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
        self.spi = pispi.Spi(mosi, miso, clk, cs, True)
        self.spi.bit_rate = 10000
        self.ce = ce
        self.pipe_address = {'0': 'ççççç', '1': 'ÂÂÂÂÂ'}
        self.pipe_dynamic = {'0': False, '1': False}
        self.irq = irq
        GPIO.setup(self.ce, GPIO.OUT)
        GPIO.setup(self.irq, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # registers=[] print('Initial state') for register in range (0x18):
        # registers.append(register) for register in registers: print(
        # f'Register {register} reads {bin(self.get(register))}')
        self.write_mask(0x00, 0b11111101, 0b10)
        self.write_mask(0x03, 0b11111100, address_width - 2)
        self.write_mask(0x05, 0b10000000, frequency)

        if air_data_rate == 0:
            self.write_mask(0x06, 0b11010111, 0xF0)
        elif air_data_rate == 2:
            self.write_mask(0x06, 0b11010111, 0xF)
        elif air_data_rate == 1:
            self.write_mask(0x06, 0b11010111, 0)

        if crc == 0:
            self.write_mask(0x00, 0b11110111, 0)
        elif crc == 1:
            self.write_mask(0x00, 0b11110011, 0b1000)
        elif crc == 2:
            self.write_mask(0x00, 0b11110011, 0b1100)

    def write(self, register, data):
        """
        Write data to a register
        :param register: int, register address
        :param data: list, int data to send
        :return: int, status register
        """
        w_register = 0b00011111 & register
        w_register = w_register | 0b00100000
        message = [w_register]
        for datum in data:
            message.append(datum)
        status = self.spi.transaction(message)
        status = int(status[:8], 2)
        return status

    def write_mask(self, register, mask, data):
        """
        Write to a portion of a register
        :param register: int, register address
        :param mask: int, mask where '0' will be modified and '1' will be held
        :param data: int, data to write
        :return: int, status register
        """
        state = self.get(register)
        state = state & mask
        data = data & (mask ^ 0xFF)
        data = state | data
        return self.write(register, [data])

    def get(self, address, buffer=1):
        """
        Read a register
        :param buffer: int, size of response (in bytes)
            does not include a status byte
        :param address: int, Register address
        :return: int, the byte stored in the `address` register

        """
        address = address & 0b00011111
        data = self.spi.transaction([address], buffer)
        return int(data[8:], 2)

    def disable_pipe(self, pipe_id):
        """
        Disable a communication pipe
        :param pipe_id: int, the pipe to be disables
        :return:
        """
        mask = 255 - (2 ** pipe_id)
        self.write_mask(0x02, mask, 0)

    def enable_pipe(self, pipe_id, pipe_address, auto_ack=True, dynamic=True,
                    payload_len=32):
        """
        Initialize a communication pipe
        :param pipe_id: int, the pipe to be initialized
        :param pipe_address: int, the address of the pipe
        :param auto_ack: bool, True: enable auto-acknowledgements, False:
            disable auto-acknowledgements
        :param dynamic: bool, True: enable dynamic payloads, False: disable
            dynamic payloads
        :param payload_len: int, the length of static payloads
        :return:
        """
        # Enable Pipe
        mask = 255 - (2 ** pipe_id)
        bit = 1 << pipe_id
        self.write_mask(0x02, mask, bit)

        # Enable/Disable AutoAck
        if auto_ack:
            self.write_mask(0x01, mask, bit)
        else:
            self.write_mask(0x01, mask, 0)

        # Set payload width
        if dynamic:
            self.pipe_dynamic[pipe_id] = True
            self.write_mask(0x1D, 0b11111011, 0b100)
            self.write_mask(0x1C, mask, bit)
            if not auto_ack:
                raise Exception
        else:
            self.pipe_dynamic[pipe_id] = False
            register = 0x11 + pipe_id
            self.write(register, [payload_len])

        # Set address
        address_width = self.get(0x03) + 2
        lsb = []
        while len(pipe_address) > 0:
            least_byte = pipe_address[-1]
            if type(least_byte) == str:
                lsb.append(ord(least_byte))
            else:
                lsb.append(least_byte)
            pipe_address = pipe_address[:-1]
        msb = lsb.copy()
        msb.reverse()
        if pipe_id != 0 and pipe_address == self.pipe_address['0']:
            raise Exception('Address cannot be the same as Pipe 0')

        if pipe_id == 1:
            bit_address = ''
            for byte in msb:
                bit_address += bin(int(byte))[2:]
            if bit_address[0:1] == '10':
                raise Exception('Address cannot start with 0b10')

            state = bit_address[0]
            shift = 0
            for bit in bit_address:
                if bit != state:
                    shift += 1
                state = bit
            if shift <= 1:
                pass
                raise Exception(
                    'address must contain more than one level shift')

        for check_pipe in self.pipe_address:
            if check_pipe != pipe_id:
                if self.pipe_address[check_pipe][-1] == msb[-1]:
                    raise Exception("LSB of pipe address must be unique")

        if not (pipe_id == 0 or pipe_id == 1):
            lsb = lsb[0]
        self.write(0x0A + pipe_id, lsb)

    def listen(self):
        """
        Wait for incoming data and report it
        :return: str, incoming data
        """
        self.write_mask(0x00, 0b11111110, 0b1)
        GPIO.output(self.ce, GPIO.HIGH)
        while GPIO.input(self.irq) == 1:
            print(self.spi.transaction([0xFF], 0))
            time.sleep(5)
        status = int(self.spi.transaction([0b11111111]), 2)
        pipe = status & 0b00001110
        pipe = pipe >> 1
        if self.pipe_dynamic[pipe]:
            message_len = self.spi.transaction(0b01100000, 1)
            message_len = message_len[8:]
            if message_len > 32:
                self.spi.transaction(0b11100010, 0)
        else:
            message_len = self.get(0x11 + pipe)
        message = self.spi.transaction(0b01100001, message_len)
        GPIO.OUT(self.ce, LOW)
        return message

    def setup_hack(self):
        """
        Copying the register data from RF24 library on Arduino
        :return:
        """
        image = {0: [0xF], 0x1: [0x3f], 0x2: [0x2], 0x3: [0x3], 0x4: [0x5f],
                 0x5: [0x4c], 0x6: [0x3], 0x7: [0xe], 0x8: [0], 0x9: [0],
                 0x0A: [49, 78, 111, 100, 101], 0x0b: [50, 78, 111, 100, 101],
                 28: [0], 29: [0]}
        for register in image:
            self.write(register, image[register])
