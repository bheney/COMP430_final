class Radio:
    def __init__(self, mosi, miso, clk, cs, ce):
        """
        Initialize an instance of an nRF24l01 transceiver
        :param mosi: int, MOSI pin
        :param miso: int, MISO pin
        :param clk: int, CLK (clock) pin
        :param cs: int, CS (chip select) pin
        :param ce: int ce pin
        """
        self.spi = pispi.Spi(mosi, miso, clk, cs, True)
        self.spi.bit_rate = 10000
        self.ce = ce
        GPIO.setup(self.ce, GPIO.OUT)
    def write(self, register,*data):
        """
        Write data to a register
        :param register: int, register address
        :param data: int, data to send
        :return: int, status register
        """
        w_register=0b00011111 & register
        w_register=w_register|0b00100000
        message=[w_register]
        for datum in data:
            message.append(datum)
        return self.spi.transaction(message)
    def write_mask(self,register,mask,data):
        """
        Write to a portion of a register
        :param register: int, register address
        :param mask: int, mask where '0' will be modified and '1' will be held
        :param data: int, data to write
        :return: int, status register
        """
        state=self.get(register)
        state=state & mask
        data=data|(~mask)
        data=state|data
        return self.write(register,data)
    def get(self, address):
        """
        Read a register
        :param address: int, Register address
        :return: int, the byte stored in the `address` register
        """
        address = address & 0b00011111
        return self.spi.transaction(address,1)

    def listen(self):
        self.write_mask(0x00,0b11111110,0b1)

All data pipes that receive data must be enabled ( EN_RXADDR register),
enable auto acknowledgement for all pipes running
Enhanced ShockBurstTM ( EN_AA register), and set the correct payload widths ( RX_PW_Px regis-
ters).
Set up addresses as described in item 2 in the Enhanced ShockBurstTM transmitting pay-
load example above.
Start Active RX mode by setting CE high.
After 130μs nRF24L01+ monitors the air for incoming communication.
When a valid packet is received (matching address and correct CRC), the payload is stored in the
RX-FIFO, and the RX_DR bit in STATUS register is set high. The IRQ pin is active when RX_DR is
high. RX_P_NO in STATUS register indicates what data pipe the payload has been received in.
If auto acknowledgement is enabled, an ACK packet is transmitted back, unless the NO_ACK bit
is set in the received packet. If there is a payload in the TX_PLD FIFO, this payload is added to
the ACK packet.
MCU sets the CE pin low to enter standby-I mode (low current mode).
MCU can clock out the payload data at a suitable rate through the SPI.
nRF24L01+ is now ready for entering TX or RX mode or power down mode.