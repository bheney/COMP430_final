"""
Receiver for a smart weather station using an intermediary Arduino
Ben Heney
12-15-22 UNH Manchester
COMP 430 Final
"""
import serial
import time


def parse_str(string, delim):
    """
    Separate the data stream from the radio
    :param string: str, the incoming data stream
    :param delim: str, the parameter to parse for
    :return:
    """
    start = string.index(delim)
    string = string[start + 1:]
    end = string.index(delim)
    string = string[:end]
    return float(string)


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM1', 115200, timeout=1)
    ser.reset_input_buffer()

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            temp = parse_str(line, "T")
            pressure = parse_str(line, "P")
            humidity = parse_str(line, "H")
            print(f'T: {temp}, P: {pressure}, H: {humidity}')

            now = time.gmtime()
            time_write = '{}-{}-{} {}:{}:{}'.format(now[2], now[1], now[0],
                                                    now[3], now[4], now[5])
            lng_log = open('wx_log.csv', 'r')
            log_mem = lng_log.read()
            lng_log.close()
            lng_log = open('wx_log.csv', 'w')
            lng_log.write(
                '{}\n{},{},{},{}'.format(log_mem, time_write, temp, pressure,
                                         humidity))
            lng_log.close()

            with open('lng_log.csv', 'r') as lng:
                last = lng.readlines()
            last = last[-1]
            last = last.split(',')
            lng_time = last[0]
            lng_type = last[1]
            lng_distance = last[2]

            website = f'<h1>Your Neck of the Woods</h1>\n<h2>Atmospheric ' \
                      f'data from {time_write}</h2>\n<p>Temperature: {temp}' \
                      f'&deg;F</p>\n<p>Pressure: {pressure} mbar</p>\n<p>RH:' \
                      f'{humidity}%</p>\n<h2>Last Lightning Activity:</h2>\n' \
                      f'<p>{lng_time} {lng_type} {lng_distance}</p> '
            with open('/var/www/html/index.html', 'w') as page:
                page.write(website)
