import serial
import io
from serial.tools.list_ports import comports

for port in comports():
    print(port)

# open the port