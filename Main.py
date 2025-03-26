import os
from serial_proto import write_read
import serial
import time

# TODO: implement try catch and 0 if unsuccessful

path = "C:/Users/selki/OneDrive/Desktop/ExtraneousFiles/18-500/flatbed-3d-scanning/scanner-controller/scanner-controller"

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

    # create normal map
    # go to this scan folder
    # TODO: Update with user-configured path
    # print directory
    # print("Current directory:", os.getcwd())
    # os.chdir(path + "/scans/scan" + str(scanID))

    os.chdir("C:/Users/selki/OneDrive/Desktop/ExtraneousFiles/18-500/flatbed-3d-scanning")

    # call normal_map.py from the command line
    print("Running normal_map.py")
    os.system("python normal_map.py --i scanner-controller/scanner-controller/scans/scan" + str(scanID) + " --o scanner-controller/scanner-controller/scans/scan" + str(scanID) + "/normal_map"+ ".png")

    return 1

run_scan(4)