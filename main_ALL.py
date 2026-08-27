# Libraries

import sys
import time
import requests
import math

# Constants

# not used
SIM = True

# Variables

progState = False

mapObj = None
playerObj = None

targetCoords = None
angleDeviation = []

# Subprograms

# Search function
def searchObj(objects, key, string, param1, param2):

    if objects == None:

        return []

    raw = [obj for obj in objects if obj.get(key) == string]

    positions = [(data[param1], data[param2]) for data in raw]

    return positions

# Angle calculator
def angleCalculator(player, target):

    px, py = player["x"], player["y"]
    dx, dy = player["dx"], player["dy"]

    tx, ty = target[0], target[1]

    # heading as current plane heading, bearing as target bearing
    heading = math.atan2(dy, dx)
    bearing = math.atan2(ty - py, tx - px)

    # calculate angular deviation in degrees and normalizes to [-180, 180] degrees
    deviation = math.degrees(heading - bearing)

    deviation = (deviation + 180) % 360 - 180

    return deviation

def exportData(data):

    with open("data.txt","w") as export:
        
        for value in data:

            export.writelines(str(value) + "\n")
    
# Main Program

while True:

    progState = False

    # try to update map data
    try:

        mapObj = requests.get("http://localhost:8111/map_obj.json", timeout = 0.5).json()

        playerObj = next((obj for obj in mapObj if obj.get("icon") == "Player"), None)
        
        targetCoords = searchObj(mapObj, "type", "bombing_point", "x", "y")

        if SIM == True:

            pass

            # functionality to come
            
        progState = True

    except:

        print("Failed to load data.")
        mapObj = None

        time.sleep(1)

        sys.exit(1)
        break

    # if data successfully imported
    if progState == True:

        angleDeviation = []

        for targets in targetCoords:

            # create and populate list of target deviation angles
            angleDeviation.append(round((angleCalculator(playerObj, targets)), 2))

        exportData(angleDeviation)

        time.sleep(2)

        print(angleDeviation)

input()

        

    
