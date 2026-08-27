# Libraries

import sys
import time
import requests
import math
import json

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Constants

# overriden by launch parameter "-sim"
SIM = False

# Flag
firstCycle = True

# Variables
mapObj = None
playerObj = None

targetCoords = None
airfieldData = None

angleDeviation = []

# Subprograms

# Server

def startServer():

    class Handler(BaseHTTPRequestHandler):

        def do_GET(self):

            if self.path == "/data":

                response = json.dumps(angleDeviation)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                self.wfile.write(response.encode())

            else:

                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            return
        
    # Port assigned as 22267
    server = HTTPServer(("127.0.0.1", 22267), Handler)

    server.serve_forever()

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

def airfieldCenter():

    combine = []
    posx = None
    posy = None
        
    start = searchObj(mapObj, "type", "airfield", "sx", "sy")
    end = searchObj(mapObj, "type", "airfield", "ex", "ey")

    for pair in range(len(start)):

        posx = (start[pair][0] + end[pair][0]) / 2
        posy = (start[pair][1] + end[pair][1]) / 2

        combine.append((posx, posy))

    return combine
    
# Main Program

if __name__ == "__main__":

    SIM = True if len(sys.argv) > 1 and sys.argv[1].lower() == "-sim" else False

    # start localhost thread
    serverThread = threading.Thread(target=startServer, daemon=True)
    serverThread.start()

    while True:

        # try to update data
        try:

            angleDeviation = []

            mapObj = requests.get("http://localhost:8111/map_obj.json", timeout = 0.5).json()

            playerObj = next((obj for obj in mapObj if obj.get("icon") == "Player"), None)
            
            targetCoords = searchObj(mapObj, "type", "bombing_point", "x", "y")

            # toggle for airfield bombing utility in simulator
            if SIM == True:

                # get airfield data once
                if firstCycle:
                    
                    airfieldData = airfieldCenter()
                    
                targetCoords.extend(airfieldData)
                
                        
            for targets in targetCoords:

                # create and populate list of target deviation angles
                angleDeviation.append(round((angleCalculator(playerObj, targets)), 2))

        except:

            print("Failed to load data.")
            mapObj = None

            time.sleep(1)

            sys.exit(1)
            break

        print(angleDeviation)

        firstCycle = False

        # delay
        time.sleep(4)

input()
