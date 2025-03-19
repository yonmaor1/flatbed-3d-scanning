import time

def write_read(x, esp):
    esp.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = esp.readline()
    return data
