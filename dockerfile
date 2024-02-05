FROM debian:latest

### first line for any debian-based linux distros update and install apt-transport-https
RUN apt update && apt install -y apt-transport-https && apt upgrade -y

## perm packages
RUN apt install -y python3 python3-pip
RUN python3 -m pip install --upgrade pip --break-system-packages
RUN python3 -m pip install 'fastapi[all]' influxdb-client --break-system-packages

WORKDIR /opt/scripts

COPY ./scripts/ /opt/scripts/

ENV INFLUXDB_URL="http://localhost:8086"
ENV INFLUX_ORG="MYORG"
ENV INFLUX_BUCKET="weatherstation"
ENV INFLUX_TOKEN="akjshdjkahskjdhakjhsdkjhjhdkj8edhfbbe4ybsbsbdfhbhdf="
ENV WEATHER_STATION_ID="station-id"
ENV WEATHER_STATION_PASSWORD="station-password"

ENV API_HOST=127.0.0.1
ENV API_PORT=8033

CMD uvicorn weatherAPI:weatherapi --port ${API_PORT} --host ${API_HOST} --reload