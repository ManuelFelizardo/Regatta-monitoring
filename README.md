# Regatta Monitoring with Drones

## Overview

Regattas are events with numerous rules governing the conduct of boats and their crews, but there are no robust means of verifying their compliance. One of the challenges posed by regattas is the environment in which they are held, which does not allow for the fixed placement of electronic monitoring devices. Drones represent an interesting solution. The objective of our project is to assist in the aerial monitoring of specific aspects of the regatta field, thus providing the collection of evidence that can be used in real time.


![alt text](https://github.com/ManuelFelizardo/Regatta-monitoring/blob/main/drone.png?raw=true)
## Project Details

## Hardware Components

### Drone (Hexacopter)
- Propellers: APC 10x5 Thin Electric
- Motors: EMP N2836/11 750 KV Brushless
- ESCs: ZTW 30 A Pro
- UBEC: Hobbywing UBEC 10/20A
- Battery: SLS XTRON 5000mAh 4S1P 14.8V 20C/40C
- Flight Controller: OpenPilot CC3D EVO
- GPS and Compass: Ublox Neo-M8N
- Frame: DJI F550
- Landing Gear: DJI F550 Landing Gear kit
- Radio Transmitter: Flysky FS-I6
- AV Transmitter: Eachine TX265
- AV Camera: Eachine 1000 TVL CCD
- AV Receiver: Eachine ROTG01 UVC OTG 5.8G 150CH

### External Processing Unit
- **Raspberry Pi 3B**
  - SoC: Broadcom BCM2837
  - CPU: 4x ARM Cortex-A53, 1.2GHz
  - GPU: Broadcom VideoCore IV
  - RAM: 1GB LPDDR2 (900 MHz)
  - Networking: 10/100 Ethernet, 2.4GHz 802.11n wireless
  - Bluetooth: Bluetooth 4.1 Classic, Bluetooth Low Energy
  - Storage: microSD
  - Ports: HDMI, 3.5mm AV jack, 4x USB 2.0, CSI, DSI
- **WiFi Adapter**: Tp-link 300Mbps - TL-WN821N USB

### Cameras
- **Front Camera**: Eachine 1000TVL CCD
- **Bottom Camera**: Raspberry Pi Camera Module V2

### GPS Trackers
- **Boats**: Android phone with location services
- **Buoys**: Nodemcu with UBLOX - NEO6M

## Software Components

### Technologies Used
- **Web Interface**: HTML5, CSS, JavaScript, jQuery, BootStrap
- **Drone Control**: Python, C++, OpenCV, FFMPEG, MQTT, UDP, INAV, Raspbian
- **Video Processing**: Picamera, H.264 encoding
- **Data Storage**: ELK stack (ElasticSearch, Logstash, Kibana), Memcached

## System Architecture

![alt text](https://github.com/ManuelFelizardo/Regatta-monitoring/blob/main/architecture.png?raw=true)

### Domain Model
- **Client**: Connects to the drone control module via a web platform. Allows for viewing video feeds, drone data, and GPS information.
- **Control Module**: Receives commands from the web platform, processes them, and controls the drone accordingly.
- **Drone Control Module**: Transforms instructions into commands for the flight controller.

### Physical Model
- **Ground Station**: Hosts the web platform (Ubuntu 16.04 LTS).
- **External GPS Trackers**: Communicate with the Raspberry Pi.
- **External Processing Unit**: Handles communication and video transmission (Raspberry Pi 3B).

### Technological Model
- **Communication**: MQTT for telemetry and commands, UDP for video transmission and GPS data.

## Code Structure

### Key Files and Their Roles

- **drone/environment.py**: Manages drone state, including position and communication with the flight controller.
- **drone/utils.py**: Utility functions for drone operations.
- **gps/gps_tracker.py**: Manages GPS data collection from Android devices.
- **gps/nodemcu_tracker.py**: Manages GPS data collection from Nodemcu devices.
- **web/server.py**: Implements the web interface and handles user interactions.
- **main.py**: Entry point for running the system.
