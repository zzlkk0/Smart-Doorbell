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
    sudo apt-get install libportaudio2 portaudio19-dev libasound2-dev
    pip install -r requirements.txt
