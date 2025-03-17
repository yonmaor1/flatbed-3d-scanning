import serial
import time

esp = serial.Serial(port='COM3', baudrate=9600, timeout=0.1)

def write_read(x):
    esp.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = esp.readline()
    return data
