import pispi
import RPi.GPIO as GPIO
mosi=16
miso=17
clk=13
csn=12
GPIO.setmode(GPIO.BCM)
GPIO.setup(csn, GPIO.OUT)
radio=pispi.Spi(mosi,miso,clk,True)
registers=[r for r in range (0x0C)]
registers.append(0x1C)
registers.append(0x1D)
for register in registers:
    if register == 0x0A or register == 0x0B:
        buffer=5
    else:
        buffer=1
    GPIO.output(csn, GPIO.LOW)
    register_result=radio.transaction([register],buffer)
    print(f'Register {hex(register)}: {register_result[8:]}')
    GPIO.output(csn, GPIO.HIGH)