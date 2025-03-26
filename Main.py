import os
from serial_proto import write_read
import serial
import time

# TODO: implement try catch and 0 if unsuccessful

# input: num is the number of rotations/scans to be performed
# output: 1 if successful, 0 if unsuccessful
def run_scan(num):

    print("Starting scanning process...")

    # move to scanner controller directory
    os.chdir("scanner-controller/scanner-controller")

    # find next num for scan folder
    scanID = 0
    for folder in os.listdir("scans"):
        if folder.startswith("scan"):
            scanID += 1

    # create new scan folder
    os.mkdir("scans/scan" + str(scanID))

    # configure port for microcontroller
    # TODO: add option to change/find port
    esp = serial.Serial(port='COM14', baudrate=9600, timeout=0.1)

    # loop through number of scans requested
    for i in range(num):
        
        # TODO: implement try catch
        # call command line dotnet run
        print("Running dotnet")
        os.system("dotnet run")
        print("Finished dotnet")

        print("Scan", i+1, "of", num, "complete.")

        # TODO: implement try catch
        write_read('d', esp) # suction
        time.sleep(0.1)
        write_read('a', esp) # rotation
        time.sleep(0.05)
        write_read('e', esp)
        print("Finished rotation")

    print("Scanning process complete.")

    return 1

run_scan(3)