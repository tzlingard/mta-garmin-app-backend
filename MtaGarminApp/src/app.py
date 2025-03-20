import json
from google.transit import gtfs_realtime_pb2
from flask import Flask, request, jsonify
import urllib
from haversine import haversine, Unit
from datetime import datetime
import pymysql

subway_lines = ['1234567s', 'ace', '7', 'bdfm', 'g', 'jz', 'l', 'nqrw']

app = Flask(__name__)

@app.route('/nearest_station_departures', methods=['GET'])
def nearest_station_departures():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    user_location = (lat, lon)
    line = request.args.get('line').lower()
    num_stations = int(request.args.get('num_stations', 3))
    
    nearest_stations = find_nearest_stations(user_location, line, num_stations)
    # Find the next num_stations (3 default) stop times from the nearest station uptown and downtown
    nearest_station, distance, next_departures = get_next_departures(line, nearest_stations)
    return jsonify({'nearest_station_name':nearest_station['stop_name'], 'distance': distance, 'arrival_times': next_departures})

def get_next_departures(line, nearest_stations, num_stations=3):
    if line in '1234567s':
        url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"
    else:
        for line_set in subway_lines:
            if line in line_set:
                url = f"https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-{line_set}"
                break
    try:
        response = urllib.request.urlopen(url)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.read())
    except urllib.error.URLError as e:
        return {'error': f"Failed to fetch data: {e.reason}"}
    except Exception as e:
        return {'error': f"An unexpected error occurred: {str(e)}"}
    arrival_times = {'uptown': [], 'downtown': []}
    for distance, nearest_station in nearest_stations.items():
        stop_id = nearest_station['stop_id'][:num_stations]
        for entity in feed.entity:
            if entity.HasField('trip_update') and entity.trip_update.trip.route_id.lower() == line.lower():
                for stop_time_update in entity.trip_update.stop_time_update:
                    if stop_id in stop_time_update.stop_id:
                        arrival_time = datetime.fromtimestamp(stop_time_update.arrival.time)
                        time_diff = (arrival_time - datetime.now()).total_seconds()
                        if time_diff > 0:
                            direction = 'uptown' if stop_time_update.stop_id[3] == 'N' else 'downtown'
                            minutes, seconds = divmod(time_diff, 60)
                            arrival_times[direction].append((int(minutes), int(seconds)))
        if len(arrival_times['uptown']) > 0 or len(arrival_times['downtown']) > 0:
            for direction in arrival_times:
                arrival_times[direction].sort(key=lambda x: (x[0], x[1]))  # Sort by minutes and then seconds
            return nearest_station, distance, arrival_times
    raise ValueError("No arrival times found for the specified line and closest stations.")
    


def find_nearest_stations(user_location, line, num_stations=3):
    nearest_stations = {}
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='mta_garmin_app'
    )
    try:
        # Create a cursor object
        with connection.cursor() as cursor:
            # Execute a query
            sql = "SELECT DISTINCT stops.stop_id, stops.stop_name, stops.stop_lat, stops.stop_lon FROM trips INNER JOIN stop_times ON stop_times.trip_id = trips.trip_id INNER JOIN stops ON stops.stop_id = stop_times.stop_id WHERE route_id = %s"
            cursor.execute(sql, (line,))
            # Fetch all results
            results = cursor.fetchall()
            # Calculate distances and store them
            for row in results:
                station_location = (row[2], row[3]) # (stop_lat, stop_lon)
                distance = haversine(user_location, station_location, unit=Unit.MILES)
                nearest_stations[distance] = {'stop_id': row[0], 'stop_name': row[1]}  # {distance: {'stop_id': stop_id, 'stop_name': stop_name}}
            # Sort by distance and get the closest stations
            nearest_stations = dict(sorted(nearest_stations.items())[:(num_stations*2)]) # get the closest stations
    finally:
        connection.close()

    return nearest_stations

def arrival_times_for_station(station_id, line):
    pass    

def get_service_alerts(line):
    line = line.lower()
    url = f"https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"
    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode())
    except urllib.error.URLError as e:
        return {'error': f"Failed to fetch data: {e.reason}"}
    except Exception as e:
        return {'error': f"An unexpected error occurred: {str(e)}"}
    
    # Beautify the JSON data
    # pretty_data = json.dumps(data, indent=4)
    # print("Service alerts:", pretty_data)
    for entity in data['entity']:        
        # if len(entity['alert']['informed_entity']) != 1:
        #     print("Alert informed entity length is not 1: " + json.dumps(entity['alert']['informed_entity'], indent=4))
        for informed_entity in entity['alert']['informed_entity']:
            if 'route_id' in informed_entity and informed_entity['route_id'].lower() == line:
                print("Alert: " + entity['alert']['header_text']['translation'][0]['text'])
                print("Description: " + entity['alert']['description_text']['translation'][0]['text'])
                # print("Start time: " + entity['alert']['active_period'][0]['start'])
                # print("End time: " + entity['alert']['active_period'][0]['end'])
                print("----------------------------------------------------------")
    # print("All good :)")

# Frontend should call the /nearest_station_departures endpoint with the user's location and the subway line letter
# The backend should return the nearest station name, the distance from the user, and the next 3 departure times uptown and downtown

# Pseudo code for the main function
# 1. Find all stations on the current line using a SQL query
# 2. Find the nearest station to the user's location using the haversine formula and save the distance
# 3. Using the real-time MTA API, retrieve the next departure times for the nearest station, uptown and downtown
# 4. Return the nearest stop name for the given line, the distance from the user, and the next departure times, uptown and downtown, in JSON format to the frontend

## TODO: Host the Flask app on a server and expose the endpoint to the frontend
## TODO: Host the MySQL database on a server, update the connection details in the app.py file, and populate the database with the create_tables script

# if __name__ == "__main__":
#     app.run(debug=True)

get_service_alerts('1')