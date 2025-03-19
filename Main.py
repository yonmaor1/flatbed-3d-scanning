import os
from serial_proto import write_read
import serial


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
    esp = serial.Serial(port='COM3', baudrate=9600, timeout=0.1)

    # loop through number of scans requested
    for i in range(num):
        
        # TODO: implement try catch
        # call command line dotnet run
        print("Running dotnet")
        os.system("dotnet run")
        print("Finished dotnet")

        print("Scan", i+1, "of", num, "complete.")

        # TODO: implement try catch
        write_read(1, esp)
        print("Finished rotation")

    print("Scanning process complete.")