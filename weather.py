#!/usr/bin/env python3

import requests
from requests.exceptions import HTTPError
from datetime import datetime as dt
from influxdb import InfluxDBClient

# https://en.wikipedia.org/wiki/Wind_direction
# https://en.wikipedia.org/wiki/Cardinal_direction

# OpenWeatherMap settings
# Docs: https://openweathermap.org/api/one-call-api
# Example API call: https://api.openweathermap.org/data/2.5/onecall?lat=33.441792&lon=-94.037689&exclude=hourly,daily&appid={API key}

OWM_API_KEY = '<YOURKEYHERE>'
OWM_LAT = 47.516347
OWM_LON = 21.600195

# possible values: OWM_EXCLUDE = ['current', 'minutely', 'hourly', 'daily', 'alerts']
OWM_EXCLUDE = ['minutely', 'alerts']

# possible values: OWM_LANG = 'hu', 'en', 'de'...
OWM_LANG = 'en'

# possible values: OWM_UNIT = 'metric', 'standard', 'imperial'
OWM_UNIT = 'metric'

# influx configuration - edit these
ifuser = "grafana"
ifpass = "<yourpassword>"
ifdb   = "openweather"
ifhost = "127.0.0.1"
ifport = 8086
#measurement_name = "weather_hourly"

datapoints = []

# connect to influx
ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)

def write_list(l: list):
    str = ''
    for elem in l:
        str = str + ',' + elem
    return str

try:
    response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={OWM_LAT}&lon={OWM_LON}&exclude={write_list(OWM_EXCLUDE)}&appid={OWM_API_KEY}&lang={OWM_LANG}&units={OWM_UNIT}')
    response.raise_for_status()
    # access JSON content
    data = response.json()
#    print("Entire JSON response")
#    print(data)

#    loop through all the elements in 'hourly' data
    for elem in data['hourly']:
        point = {
                'measurement': 'weather_hourly',
                'time': dt.fromtimestamp(elem['dt']),
                'tags': {
                        'location': 'Debrecen',
                        'source': 'Adam'
                },
                'fields': {
                        'temp': float(elem['temp']),
                        'feels_like':float(elem['feels_like']),
                        'wind_speed': float(elem['wind_speed']),
                        'wind_deg': elem['wind_deg']
                }
        }
        datapoints.append(point)

#    loop through all the elements in 'daily' data
    for elem in data['daily']:
        point = {
                'measurement': 'weather_daily',
                'time': dt.fromtimestamp(elem['dt']),
                'tags': {
                        'location': 'Debrecen',
                        'source': 'Adam'
                },
                'fields': {
                        'temp_min': float(elem['temp']['min']),
                        'temp_max': float(elem['temp']['max']),
                        'pop': float(elem['pop']),
                        'uvi': float(elem['uvi']),
                        'sunrise': elem['sunrise'],
                        'sunset': elem['sunset']
                }
        }
        datapoints.append(point)

#    loop through the first 3 elements in 'hourly' data
#    for i in range(3):
#        print(dt.fromtimestamp(data['hourly'][i]['dt']))

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')

# write the measurement
ifclient.write_points(datapoints)
