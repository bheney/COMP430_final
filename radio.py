import pispi


class Radio:
    def __init__(self, mosi, miso, clk, cs, ce, irq, address_width=5,
                 frequency=2, air_data_rate=1, lna_gain=0):
        """
        Initialize an instance of an nRF24l01 transceiver
        :param mosi: int, MOSI pin
        :param miso: int, MISO pin
        :param clk: int, CLK (clock) pin
        :param cs: int, CS (chip select) pin
        :param ce: int ce pin
        :param irq: int, interrupt pin
        """
        self.spi = pispi.Spi(mosi, miso, clk, cs, True)
        self.spi.bit_rate = 10000
        self.ce = ce
        self.pipe_address = {'0': 0xE7E7E7E7E7, '1': 0xC2C2C2C2C2}
        self.pipe_dynamic = {'0': False, '1': False}
        self.irq = irq
        GPIO.setup(self.ce, GPIO.OUT)
        GPIO.setup(self.irq, GPIO.IN)

    def write(self, register, *data):
        """
        Write data to a register
        :param register: int, register address
        :param data: int, data to send
        :return: int, status register
        """
        w_register = 0b00011111 & register
        w_register = w_register | 0b00100000
        message = [w_register]
        for datum in data:
            message.append(datum)
        status=self.spi.transaction(message)
        status=int(status[:8],2)
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
        data = data | (~mask)
        data = state | data
        return self.write(register, data)

    def get(self, address):
        """
        Read a register
        :param address: int, Register address
        :return: int, the byte stored in the `address` register
        """
        address = address & 0b00011111
        data = self.spi.transaction(address, 1)
        return int(data[:8],2)

    def enable_pipe(self, pipe_id, pipe_address, auto_ack=True, dynamic=True,
                    payload_len=32):
        # Enable Pipe
        mask = (254 + 1) - (2 ^ pipe_id)
        bit = 1 << pipe_id
        self.write_mask(0x02, mask, bit)

        # Enable/Disable AutoAck
        if auto_ack:
            self.write_mask(0x01, mask, bit)
        else:
            self.write_mask(0x01, mask, ~bit)

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
            self.write(register, payload_len)

        # Set address
        address_width = self.get(0x03) + 2
        msb = pipe_address.to_bytes(address_width, 'big')
        lsb = pipe_address.to_bytes(address_width, 'little')
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
                raise Exception(
                    'address must contain more than one level shift')

        for check_pipe in self.pipe_address:
            address = self.pipe_address[check_pipe]
            check_address_bytes = address.to_bytes(address_width, 'big')
            if check_pipe != pipe_id:
                if check_address_bytes[-1] == msb[-1]:
                    raise Exception("LSB of pipe address must be unique")

        if not (pipe_id == 0 or pipe_id == 1):
            lsb = lsb[0]
        self.write(0x0A + pipe_id, lsb)

    def listen(self):
        self.write_mask(0x00, 0b11111110, 0b1)
        GPIO.OUT(self.ce, HIGH)
        while self.irq == 0:
            pass
        status = self.spi.transaction(0b11111111)
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
