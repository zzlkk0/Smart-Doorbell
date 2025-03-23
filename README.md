
# Smart Door Access System

This project integrates two core modules: a **Smart Doorbell & Control System** and a **Face Recognition System**. Together, they provide secure and intelligent access control for homes, offices, or IoT projects.

---

## 🧠 Features

### 🔔 Smart Doorbell & Control System
- OLED status display
- Four physical buttons for recording, calling, doorbell, and door control
- Audio streaming via RTMP
- MQTT integration for remote control and status reporting
- Servo motor door unlock
- Local and remote doorbell triggering
- Audio recording and transfer over TCP

### 🧑‍💻 Face Recognition System
- Real-time face detection using Haar Cascades
- Face recognition using LBPH (Local Binary Pattern Histogram)
- Whitelist and blacklist filtering
- Stranger detection with image logging
- Multi-threaded frame capture and recognition
- Optional MQTT messaging for integration

---

## 📦 Prerequisites

- **Hardware**: Raspberry Pi or similar SBC, OLED (SSD1306), 4 buttons, servo motor, speaker, mic, camera or RTMP source
- **Software**:
  ```bash
  pip install opencv-contrib-python numpy paho-mqtt smbus luma.oled gpiozero pyaudio
  ```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/zzlkk0/Smart-Doorbell.git
cd Smart-Doorbell
```

### 2. Configure the System
- Edit IP addresses, GPIO pins, and MQTT topics in the scripts.
- Update `whitelist.txt` and `blacklist.txt` with recognized names.

### 3. Run Modules
- **Face Recognition**:
  ```bash
  python \FaceRecognition\faceselect2.py
  ```
- **Doorbell Control**:
  ```bash
  python \SmartDoorBell\door8.py
  ```

---

## 📡 MQTT Topics

| Topic                         | Direction | Payload | Action                  |
|------------------------------|-----------|---------|-------------------------|
| /homeassistant/sent/door     | IN        | 1       | Unlock the door         |
| /homeassistant/sent/light    | IN        | 1/0     | Toggle status LED       |
| /homeassistant/sent/bell     | IN        | 1       | Trigger doorbell sound  |
| /homeassistant/recording     | OUT       | 1/0     | Notify recording status |

---

## 📷 Stranger Logging

- Unknown faces detected for over 10 seconds will be saved as `.jpg` files automatically.
- Detection pauses after repeated recognition to avoid flooding.

---

## 🛠 License

MIT License (or your preferred license)

---

## 🙌 Contribution

Pull requests and suggestions are welcome! Feel free to open an issue or fork the project.
