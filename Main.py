import os
import subprocess
import sys
from serial_proto import write_read
import serial
import time

# TODO: implement try catch and 0 if unsuccessful

# input: num is the number of rotations/scans to be performed
# output: 1 if successful, 0 if unsuccessful
def run_scan(num, path, dpi):

    print("Starting scanning process...")

    # move to scanner controller directory
    os.chdir("scanner-controller/scanner-controller")

    # find next num for scan folder
    scanID = 0

    # create scan directory if can't find it
    try:
        for folder in os.listdir("scans"):
            if folder.startswith("scan"):
                scanID += 1
    except:
        print("Scans folder not found. Creating new scans folder.")
        os.mkdir("scans")

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
        subprocess.run(["dotnet", "run", "--", str(dpi)], check=True)
        print("Finished dotnet")

        print("Scan", i+1, "of", num, "complete.")

        # TODO: implement try catch
        write_read('d', esp) # suction
        time.sleep(0.1)
        write_read('a', esp) # rotation
        time.sleep(0.05)
        write_read('e', esp)
        print("Finished rotation")

    time.sleep(0.5)
    write_read('b', esp) # rotate back
    time.sleep(0.5)
    print("Scanning process complete.")

    # create normal map
    # go to this scan folder
    os.chdir(path)

    # call normal_map.py from the command line
    print("Running normal_map.py")
    os.system("python normal_map.py --i scanner-controller/scanner-controller/scans/scan" + str(scanID) + " --o scanner-controller/scanner-controller/scans/scan" + str(scanID) + "/normal_map"+ ".png")

    return 1

if __name__ == "__main__":
  num = int(sys.argv[1])
  path = sys.argv[2]
  dpi = int(sys.argv[3])
  run_scan(num, path, dpi)