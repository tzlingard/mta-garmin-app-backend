import sys
import os
from flask import Flask 

# Add the path to the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import find_nearest_stations, get_next_departures, app

def unit_test():
    print("Unit test")
    line = '3'
    line = line.lower()
    # Find the nearest station on the current line
    nearest_stations = find_nearest_stations((40.7600019, -73.9916988), line)
    # Find the next 3 stop times from the nearest station uptown and downtown
    nearest_station, distance, next_departures = get_next_departures(line, nearest_stations)
    # print("Nearest station:", nearest_station)
    # print("Distance:", distance)
    # print("Next departures:", next_departures)
    # print(f"Nearest station: {nearest_station['stop_name']}")
    for direction in next_departures:
        print(f"{direction.capitalize()}:")
        for minutes, seconds in next_departures[direction]:
            print(f"{minutes} min {seconds} sec")

def contract_test():
    print("Contract test")
    response = app.test_client().get('/nearest_station_departures?lat=40.7600019&lon=-73.9916988&line=3')
    print(response.data)

if __name__ == "__main__":
    unit_test()
    contract_test()
