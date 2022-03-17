# Klax-Dashboard

Simple Klax 2.0 Iot Device Dashboard (Energy Meter). Onboarded by TTN

# Installation

```
docker pull omza/klaxdashboard

docker run --env-file ./.env --name klaxv2 -p 8000:80 -v /var/opt/klax:/var/opt/klax --network="root_default" -d omza/klaxdashboard
```
