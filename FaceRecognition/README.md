
# Face Recognition System User Manual

This document provides an overview, setup instructions, and usage guide for the Face Recognition System. The system uses OpenCV for face detection and recognition, along with MQTT for remote communication.

---

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Code Explanation](#code-explanation)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

This Face Recognition System performs real-time face detection and recognition by:
- Capturing video from a live RTMP stream
- Detecting faces using a Haar Cascade classifier
- Recognizing faces using LBPH (Local Binary Pattern Histogram)
- Differentiating between whitelisted, blacklisted, and unknown individuals
- Saving snapshots of strangers after prolonged presence
- Optionally publishing results via MQTT

![Description](images/doorbell.jpg)

---

## Prerequisites

### Hardware
- A computer or SBC (e.g., Raspberry Pi) capable of video processing
- A camera or an RTMP video stream source

### Software
- Python 3.x
- OpenCV (with contrib modules for face recognition)
- NumPy
- Paho-MQTT
- smbus (optional, for I2C)
- Standard libraries: `threading`, `queue`, `time`

---

## Installation

1. **Install Python 3.x**

2. **Install Dependencies**

   Use pip to install the required libraries:
   ```bash
   pip install opencv-contrib-python numpy paho-mqtt smbus
   ```

3. **Clone the Repository**

   If hosted on GitHub:
   ```bash
   git clone https://github.com/zzlkk0/Smart-Doorbell.git
   cd Smart-Doorbell\FaceRecognition
   ```

---

## Configuration

### RTMP Stream
Update the RTMP stream URL in the code:
```python
self.cap = cv2.VideoCapture('rtmp://192.168.1.115:8888/live1/stream')
```

### Face Recognition Model & Cascade
- `face_cascade_path`: Path to Haar Cascade XML file (e.g., `haarcascade_frontalface_default.xml`)
- `model_path`: Trained model file (e.g., `trainer/trainer.yml`)

### Whitelist / Blacklist
Create `whitelist.txt` and `blacklist.txt`, one name per line.

### MQTT Setup
Modify MQTT server settings:
```python
mqtt_addr = "192.168.1.115"
port = 1883
```

---

## Usage

Run the program from terminal:
1. Capture enough white list faces:
```bash
python facecap.py
```
2. Train the recognition model from your white list:
```bash
python trainer_model.py
```
   
3. Run face recognition main functionL:
```bash
python faceselect2.py
```

It will:
- Start capturing frames from the RTMP stream
- Detect and recognize faces
- Log or save stranger images after 10 seconds
- Show real-time results in a GUI window

Press `Esc` to exit.

---

## Code Explanation

- **FaceRecognizer Class**  
  Loads Haar Cascade, the LBPH model, and whitelist/blacklist names.  
  Uses threading for concurrent video capture and processing.  
  - `capture_frames`: captures and queues frames
  - `process_frames`: detects and recognizes faces  
    - Logs detection
    - Saves unknown faces if present for 10 seconds
    - Manages detection pause to avoid repeated detection

- **MQTT (Optional)**  
  The MQTT client is included and can be expanded for remote integration.

---

## Troubleshooting

| Issue                  | Solution                                                   |
|------------------------|------------------------------------------------------------|
| Cannot read RTMP stream| Check the RTMP URL and ensure the stream is online         |
| Poor recognition       | Check model quality and retrain with better samples        |
| No GUI output          | Ensure OpenCV supports GUI on your system (headless issues)|

---

## License

Add your license information here.
