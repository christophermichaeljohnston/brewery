# brewery

Arduino and Raspberry PI powered brewery.

Manage connected brewery devices (only fermenter at this time, two of them)
and provides graphs of collected temperatures.

# run it

docker-compose build
docker-compuse up -d

# notes

Whenever adding or removing new usb devices, need to restart the docker
container to also see it. Need to figure this out. 
