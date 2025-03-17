import os
import time
from serial_proto import write_read


def run_scan(num):

    print("Starting scanning process...")

    # move to scanner controller directory
    os.chdir("scanner-controller/scanner-controller")

    # find next num for scan folder
    scanID = 0
    for folder in os.listdir():
        if folder.startswith("scan"):
            scanID += 1

    # create new scan folder
    os.mkdir("scan" + str(scanID))

    # loop through number of scans requested
    for i in range(num):
        
        # TODO: implement try catch
        # call command line dotnet run
        print("Running dotnet")
        os.system("dotnet run")
        print("Finished dotnet")

        print("Scan", i+1, "of", num, "complete.")

        # TODO: implement try catch
        write_read(1)
        print("Finished rotation")

    print("Scanning process complete.")