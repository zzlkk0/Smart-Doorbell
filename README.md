# Smart-Doorbell
A backend program for controlling door opening operations, integrating MQTT communication to control door opening actions, making voice calls and recording messages with the Android end, adding face recognition functions and basic doorbell functions.

# Smart Door Control System User Manual

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Hardware Setup](#hardware-setup)
- [Functionality Guide](#functionality-guide)
  - [Doorbell Operation](#doorbell-operation)
  - [Call Management](#call-management)
  - [Audio Recording](#audio-recording)
  - [Door Control](#door-control)
- [MQTT Integration](#mqtt-integration)
- [Troubleshooting](#troubleshooting)
- [Safety & Best Practices](#safety--best-practices)

---

## Overview
This system integrates an OLED display, physical buttons, audio I/O, and network protocols to enable:
- Voice calls over UDP/TCP
- Audio recording/playback
- Doorbell activation
- Door control via servo motor
- Remote control via MQTT

---

## Prerequisites
- **Hardware**:
  - Raspberry Pi (or similar SBC)
  - SSD1306 OLED (I2C interface)
  - 4x Tactile buttons
  - Microphone & Speaker
  - Servo motor (door control)
  - LED (status light)
- **Software**:
  - Python 3.7+
  - Required libraries:
    ```bash
    pip install luma.oled gpiozero pyaudio paho-mqtt smbus
    ```

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://example.com/smart-door-system.git
   cd smart-door-system
2. Install dependency：
   ```bash
    sudo apt-get install libportaudio2 portaudio19-dev libasound2-dev
    pip install -r requirements.txt

## Configuration
# Network Settings

# UDP Server (Modify in script)
udp_server_address = ('192.168.211.51', 8699)

# TCP Server (Audio transfer)
tcp_server_address = ('192.168.211.51', 8700)

# MQTT Broker
MQTT_BROKER = "192.168.1.115"
MQTT_PORT = 1883
# Audio Settings

# RTMP Stream (Modify for your audio server)
audio_player = VLCAudioPlayer("rtmp://0.0.0.0:8889/live2/stream")

# Doorbell Sound File Path
DOORBELL_SOUND = "/home/user/doorbell/doorbell.wav"
Hardware Setup
Component	GPIO Pin
Button 1 (Rec)	21
Button 2 (Call)	27
Button 3 (Bell)	22
Button 4 (Door)	23
LED	16
Servo Motor	13


## Functionality Guide
# Doorbell Operation
Local Trigger
Press Button 3 (GPIO 22):
OLED displays:
Doorbell 
ringing
# System behavior:
Lowers speaker volume to 50%
Plays doorbell.wav
Restores original volume after playback
Returns to default screen after 2 seconds
# Remote Trigger
Send MQTT message to /homeassistant/sent/bell:
mosquitto_pub -h 192.168.1.115 -t "/homeassistant/sent/bell" -m "1"
Call Management
# Placing a Call
Press Button 2 (GPIO 27):

OLED shows: Calling...

UDP sends CALL_REQUEST to server

10-second timeout countdown begins

Accepting a Call
Remote System Response:

Server sends ACCEPT_CALL via UDP

Local system:

OLED updates to Call answered

Starts RTMP audio stream

Displays call duration: Talking 15s

Ending a Call
Local Termination:

Press Button 2 again

OLED shows Call ended

Sends HANG_UP via UDP

Remote Termination:

Server sends HANG_UP command

System auto-terminates call

Audio Recording
Press Button 1 (GPIO 21):

OLED displays:

复制
Recording...
10-second recording starts

Saved as output1.wav

Auto-uploaded via TCP to server

Door Control
Local Operation
Press Button 4 (GPIO 23):

Sends OPEN_DOOR_REQUEST via UDP

OLED confirmation:

复制
Open request 
has been sent
Remote Operation
Send MQTT command:

bash
复制
mosquitto_pub -h 192.168.1.115 -t "/homeassistant/sent/door" -m "1"
Servo motor opens door (90° position)

LED turns on during operation

MQTT Integration
Topic	Direction	Payload	Action
/homeassistant/sent/door	IN	1	Triggers door opening
/homeassistant/sent/light	IN	1/0	Controls LED (GPIO 16)
/homeassistant/sent/bell	IN	1	Remote doorbell trigger
/homeassistant/recording	OUT	1/0	Recording status updates
Troubleshooting
Issue	Solution
Doorbell not sounding	1. Verify doorbell.wav exists
2. Check audio permissions: sudo usermod -a -G audio pi
Call audio distortion	1. Confirm RTMP server is running
2. Check network latency with ping 192.168.1.115
OLED display blank	1. Run i2cdetect -y 1 to verify I2C address
2. Check soldering connections
MQTT connection failure	1. Verify broker IP/port
2. Check firewall settings: sudo ufw allow 1883
Safety & Best Practices
Electrical Safety:

Use 3.3V logic level for GPIO

Add 1kΩ resistors in series with buttons

Servo Maintenance:

Lubricate gears quarterly

Avoid continuous operation >15 seconds

Software Updates:

bash
复制
sudo apt-get update && sudo apt-get upgrade
pip freeze --local | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
Emergency Stop:

Add hardware kill switch between Pi and motor power supply
