import os
import time
import shutil


def run_scan(num):

    # loop through number of scans requested
    for i in range(num):
        print("Starting scanning process...")

        # TODO: implement try catch
        # move to scanner controller directory
        os.chdir("scanner-controller/scanner-controller")

        # find next num for scan folder
        scanID = 0
        for folder in os.listdir():
            if folder.startswith("scan"):
                scanID += 1

        # create new scan folder
        os.mkdir("scan" + str(scanID))

        # call command line dotnet run
        print("Running dotnet")
        os.system("dotnet run")
        print("Finished dotnet")

        # move back to main directory
        os.chdir("../..")

        print("Scan", i+1, "of", num, "complete.")

        # TODO: rotate object through microcontroller call