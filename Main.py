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

    write_read('d', esp) # suction

    # loop through number of scans requested
    for i in range(num):
        
        # TODO: implement try catch
        # call command line dotnet run
        print("Running dotnet")
        subprocess.run(["dotnet", "run", "--", str(dpi)], check=True)
        print("Finished dotnet")

        print("Scan", i+1, "of", num, "complete.")

        # TODO: implement try catch
        
        time.sleep(0.1)
        write_read('a', esp) # rotation
        time.sleep(0.05)
        print("Finished rotation")

    write_read('e', esp) # turn off suction

    time.sleep(0.5)
    write_read('b', esp) # rotate back
    time.sleep(0.5)
    print("Scanning process complete.")

    # create normal map
    # go to this scan folder
    os.chdir(path)

    # align scans
    print("Running align.py")
    subprocess.run("python align.py scanner-controller/scanner-controller/scans/scan" + str(scanID))

    # call normal_map.py from the command line
    print("Running normal_map.py")
    subprocess.run("python normal_map.py --i scanner-controller/scanner-controller/scans/scan" + str(scanID) + "/aligned --o scanner-controller/scanner-controller/scans/scan" + str(scanID) + "/normal_map"+ ".png")

    # check if normal map was created
    if not os.path.exists("scanner-controller/scanner-controller/scans/scan" + str(scanID) + "/normal_map.png"):
        print("Normal map creation failed.")
        return 0
    
    normal_map_path = f"scanner-controller/scanner-controller/scans/scan{scanID}/normal_map.png"
    height_map_path = f"scanner-controller/scanner-controller/scans/scan{scanID}/height_map.png"

    # convert normal map to height map
    print("Running normal_to_height.py")
    subprocess.run([
        "python", "normal_to_height.py", normal_map_path, height_map_path, "--seamless", "FALSE"
    ], check=True)

    print("Normal map converted to height map.")

    # create model
    # print("Running height_to_3d.py")
    # subprocess.run("python height_to_3d.py " + str(scanID), shell=True)

    print(scanID)

    # return scanID

if __name__ == "__main__":
  num = int(sys.argv[1])
  path = sys.argv[2]
  dpi = int(sys.argv[3])
  scanID = run_scan(num, path, dpi)
  print(scanID)