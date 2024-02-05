from datetime import datetime
import sys
import os
from fastapi import FastAPI,Request,HTTPException
from typing import List
from pydantic import BaseModel, Field
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUXDB_URL = "http://localhost:8086"
if("INFLUXDB_URL" in os.environ):
    INFLUXDB_URL = os.environ['INFLUXDB_URL']

INFLUX_ORG = "MyORG"
if("INFLUX_ORG" in os.environ):
    INFLUX_ORG = os.environ["INFLUX_ORG"]

INFLUX_BUCKET = "weatherstation"
if("INFLUX_BUCKET" in os.environ):
    INFLUX_BUCKET = os.environ["INFLUX_BUCKET"]

INFLUX_TOKEN = "sjkhdakjshdjkhakshdjahkjsdhkjahskjd"
if("INFLUX_TOKEN" in os.environ):
    INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]

WEATHER_STATION_ID = "station-id"
if("WEATHER_STATION_ID" in os.environ):
    WEATHER_STATION_ID = os.environ['WEATHER_STATION_ID']

WEATHER_STATION_PASSWORD = "station-password"
if("WEATHER_STATION_PASSWORD" in os.environ):
    WEATHER_STATION_PASSWORD = os.environ['WEATHER_STATION_PASSWORD']

class updateInflux:

    def __init__(self,url,token,org,bucket):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        try:
            self.client = influxdb_client.InfluxDBClient(
                        url=self.url,
                        token=self.token,
                        org=self.org
                )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        except:
            sys.exit("Unable to connect to InfluxDB")

    def health(self):
        health = self.client.health()
        if health.status == "pass":
            return True
        return False
    
    def setMeasurement(self,name):
        self.data = influxdb_client.Point(name)

    def putTag(self,key,value):
        self.data.tag(key,value)

    def putField(self,key,value):
        self.data.field(key,value)

    def get(self,query):
        tables = self.client.query_api().query(query)
        return tables.to_values(columns=['_value'])

    def commit(self):
        self.write_api.write(bucket=self.bucket, org=self.org, record=self.data)

def fehrenheitToCelsius(temp):
    return (temp - 32) * 5/9

def mphToKmh(mph):
    return (mph * 1.60934)

def cardinalPoints(angle):
    cardinal = None
    if( angle >= 348.75 and angle <= 360 ):
          cardinal = "N"
    elif( angle >= 0 and angle <= 11.249 ):
          cardinal = "N"
    elif( angle >= 11.25 and angle <= 33.749 ):
          cardinal = "N NO"
    elif( angle >= 33.75 and angle <= 56.249 ):
          cardinal = "NO"
    elif( angle >= 56.25 and angle <= 78.749 ):
          cardinal = "S NS"
    elif(angle >= 78.75 and angle <= 101.249 ):
          cardinal = "S"
    elif(angle >= 101.25 and angle <= 123.749 ):
          cardinal = "S ES"
    elif(angle >= 123.75 and angle <= 146.249 ):
          cardinal = "ES"
    elif(angle >= 146.25 and angle <= 168.749 ):
          cardinal = "N"
    elif(angle >= 168.75 and angle <= 191.249 ):
          cardinal = "E"
    elif(angle >= 191.25 and angle <= 213.749 ):
          cardinal = "E EW"
    elif(angle >= 213.75 and angle <= 236.249 ):
          cardinal = "EW"
    elif(angle >= 236.25 and angle <= 258.749 ):
          cardinal = "W EW"
    elif(angle >= 258.75 and angle <= 281.249 ):
          cardinal = "W"
    elif(angle >= 281.25 and angle <= 303.749 ):
          cardinal = "W NW"
    elif(angle >= 303.75 and angle <= 326.249 ):
          cardinal = "NW"
    elif(angle >= 326.25 and angle <= 348.749 ):
          cardinal = "N NW"
    return cardinal

weatherapi = FastAPI(
    title="Bresser Weather station 7in1",
    description="Get weather station information"
)

influx = updateInflux(
    url=INFLUXDB_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG,
    bucket=INFLUX_BUCKET
)

@weatherapi.get("/weatherstation/updateweatherstation.php",
    tags=['WeatherStationUpdate'],
    summary="weather station get requests",
    description="weather information"
)
async def weather_update(request: Request):
    params = dict(request.query_params)
    if(params):
        if('ID' in params and 'PASSWORD' in params):
            if(params['ID'] == WEATHER_STATION_ID and params['PASSWORD'] == WEATHER_STATION_PASSWORD):

                curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if('baromin' in params):
                    influx.setMeasurement('barometer')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('baromin', float(params['baromin']))
                    influx.commit()

                if('tempf' in params):
                    influx.setMeasurement('temp')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('celsius', fehrenheitToCelsius(float(params['tempf'])))
                    influx.putField('fehrenheit',float(params['tempf']))
                    influx.commit()

                if('dewptf' in params):
                    influx.setMeasurement('dewpoint')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('celsius', fehrenheitToCelsius(float(params['dewptf'])))
                    influx.putField('fehrenheit',float(params['dewptf']))
                    influx.commit()

                if('humidity' in params):
                    influx.setMeasurement('humidity')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('humidity', float(params['humidity']))
                    influx.commit()

                if('windspeedmph' in params):
                    influx.setMeasurement('wind')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('windspeedkmh', mphToKmh(float(params['windspeedmph'])))
                    influx.commit()

                if('windgustmph' in params):
                    influx.setMeasurement('wind')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('windgustkmh', mphToKmh(float(params['windgustmph'])))
                    influx.commit()

                if('winddir' in params):
                    influx.setMeasurement('wind')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('winddir',float(params['winddir']))
                    influx.putField('cardinal',cardinalPoints(float(params['winddir'])))
                    influx.commit()

                if('rainin' in params):
                    influx.setMeasurement('rain')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('rainin',float(params['rainin']))               
                    influx.commit()

                if('dailyrainin' in params):
                    influx.setMeasurement('rain')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('dailyrainin',float(params['dailyrainin']))
                    influx.commit()

                if('solarradiation' in params):
                    influx.setMeasurement('solarradiation')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('solarradiation',float(params['solarradiation']))
                    influx.commit()

                if('solarradiation' in params):
                    influx.setMeasurement('solarradiation')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('UV',float(params['UV']))
                    influx.commit()

                if('indoortempf' in params):
                    influx.setMeasurement('indoor')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('celsius',fehrenheitToCelsius(float(params['indoortempf'])))
                    influx.commit()

                if('indoorhumidity' in params):
                    influx.setMeasurement('indoor')
                    influx.putTag('ID',params['ID'])
                    influx.putTag('timestamp',curdate)
                    influx.putField('humidity',float(params['indoorhumidity']))
                    influx.commit()

                return params
            else:
                return HTTPException(403,'incorect credentials')
        else:
            return HTTPException(403,'no credentials')
    return HTTPException(500)

#if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(weatherapi, host="0.0.0.0", port=8000)