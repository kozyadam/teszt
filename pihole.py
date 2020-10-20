#!/usr/bin/env python3

import requests
from requests.exceptions import HTTPError
from datetime import datetime as dt
from influxdb import InfluxDBClient

# influx configuration - edit these
ifuser = "grafana"
ifpass = "<yourpassword>"
ifdb   = "pihole"
ifhost = "127.0.0.1"
ifport = 8086

datapoints = []

try:
    response = requests.get('http://localhost/admin/api.php')
    response.raise_for_status()
    # access JSON content
    data = response.json()
#    print("Entire JSON response")
#    print(data)

#    loop through all the elements in 'hourly' data
    point = {
        'measurement': 'pihole_data',
        'time': dt.now(),
        'fields': {
                'ads_blocked_today': data['ads_blocked_today'],
        }
    }
    datapoints.append(point)

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')

# write the measurement
ifclient.write_points(datapoints)
