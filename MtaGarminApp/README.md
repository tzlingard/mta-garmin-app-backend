# MTA Garmin App

This project is a Python application that retrieves real-time subway data from the MTA GTFS API and decodes it using Protocol Buffers (protobuf). It provides an API endpoint to get the nearest subway station to the user on the desired line and the next departure times. If the closest station has no arrival times listed, the next 2 closest stations are checked.

## Project Structure

```
MtaGarminApp
├── src
│   ├── app.py                # Main entry point of the application
│   └── create_tables.py      # Script to create and populate the SQL database
├── tests
│   └── test_app.py           # Unit and contract tests
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd MtaGarminApp
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Spin up a local MySQL database using Docker:
   ```
   docker run --name local-mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=mta_garmin_app -p 3306:3306 -d mysql:latest
   ```

5. Create and populate the SQL database:
   ```
   python src/create_tables.py
   ```

## Usage

To run the application, execute the following command:
```
python src/app.py
```

This will start the Flask server. You can then use the API endpoint to get the nearest subway station and the next departure times.

### API Endpoint

#### `GET /nearest_station_departures`

Retrieve the nearest subway station and the next departure times.

**Parameters:**
- `lat` (float): Latitude of the user's location.
- `lon` (float): Longitude of the user's location.
- `line` (str): Subway line (e.g., '3', 'A', 'L').

**Example Request:**
```
GET /nearest_station_departures?lat=40.7600019&lon=-73.9916988&line=3
```

**Example Response:**
```json
{
  "nearest_station_name": "Times Sq - 42 St",
  "distance": 0.2,
  "arrival_times": {
    "uptown": [
      [3, 45],
      [10, 30]
    ],
    "downtown": [
      [5, 15],
      [12, 50]
    ]
  }
}
```
The values returned for arrival times reflect minutes and seconds respectively. For the above example, an uptown 3 train is leaving from Times Square in 3 minutes 45 seconds as well as in 10 minutes 30 seconds, and a downtown train is arriving in 5 minutes 15 seconds and 12 minutes 50 seconds.

## Dependencies

This project requires the following Python packages:
- `flask` for creating the API endpoint
- `haversine` for calculating distances
- `pymysql` for database interactions

Make sure to install these packages using the `requirements.txt` file.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.