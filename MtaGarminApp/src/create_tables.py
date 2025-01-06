import pandas as pd
import pymysql
import os 

# Database connection details
db_host = 'localhost'
db_user = 'root'
db_password = 'root'
db_name = 'mta_garmin_app'

# Connect to the database
connection = pymysql.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

# Get the current directory
current_dir = os.path.dirname(__file__)

# Read the CSV files
stops_data = pd.read_csv(os.path.join(current_dir, 'stops.txt'))
trips_data = pd.read_csv(os.path.join(current_dir, 'trips.txt'))
stop_times_data = pd.read_csv(os.path.join(current_dir, 'stop_times.txt'))

# Replace NaN values with None
stops_data = stops_data.where(pd.notnull(stops_data), None)
trips_data = trips_data.where(pd.notnull(trips_data), None)
stop_times_data = stop_times_data.where(pd.notnull(stop_times_data), None)

# Create the SQL tables if they do not exist
create_stops_table = """
CREATE TABLE IF NOT EXISTS stops (
    stop_id VARCHAR(255) PRIMARY KEY,
    stop_name VARCHAR(255),
    stop_lat FLOAT,
    stop_lon FLOAT
);
"""


create_trips_table = """
CREATE TABLE IF NOT EXISTS trips (
    trip_id VARCHAR(255) PRIMARY KEY,
    route_id VARCHAR(255),
    service_id VARCHAR(255),
    trip_headsign VARCHAR(255),
    direction_id INT,
    shape_id VARCHAR(255) NULL
);
"""

create_stop_times_table = """
CREATE TABLE IF NOT EXISTS stop_times (
    trip_id VARCHAR(255),
    stop_id VARCHAR(255),
    arrival_time TIME,
    departure_time TIME,
    stop_sequence INT,
    PRIMARY KEY (trip_id, stop_id, stop_sequence)
);
"""

with connection.cursor() as cursor:
    cursor.execute(create_stops_table)
    cursor.execute(create_trips_table)
    cursor.execute(create_stop_times_table)
    connection.commit()

# Insert data into the SQL tables
stops_insert_query = """
INSERT INTO stops (stop_id, stop_name, stop_lat, stop_lon)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    stop_name = VALUES(stop_name),
    stop_lat = VALUES(stop_lat),
    stop_lon = VALUES(stop_lon);
"""

trips_insert_query = """
INSERT INTO trips (trip_id, route_id, service_id, trip_headsign, direction_id, shape_id)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    route_id = VALUES(route_id),
    service_id = VALUES(service_id),
    trip_headsign = VALUES(trip_headsign),
    direction_id = VALUES(direction_id),
    shape_id = VALUES(shape_id);
"""

stop_times_insert_query = """
INSERT INTO stop_times (trip_id, stop_id, arrival_time, departure_time, stop_sequence)
VALUES (%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    arrival_time = VALUES(arrival_time),
    departure_time = VALUES(departure_time),
    stop_sequence = VALUES(stop_sequence);
"""

with connection.cursor() as cursor:
    for _, row in stops_data.iterrows():
        cursor.execute(stops_insert_query, (row['stop_id'], row['stop_name'], row['stop_lat'], row['stop_lon']))
    
    for _, row in trips_data.iterrows():
        cursor.execute(trips_insert_query, (row['trip_id'], row['route_id'], row['service_id'], row['trip_headsign'], row['direction_id'], row['shape_id']))
    
    for _, row in stop_times_data.iterrows():
        cursor.execute(stop_times_insert_query, (row['trip_id'], row['stop_id'], row['arrival_time'], row['departure_time'], row['stop_sequence']))
    
    connection.commit()

# Close the connection
connection.close()