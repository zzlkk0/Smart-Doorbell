
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

# 🔧 RTMP Streaming Setup with FFmpeg and Nginx

This guide describes how to set up video/audio streaming using `ffmpeg` and an Nginx RTMP server.

---

## 🚀 Start Nginx Server

```bash
sudo /usr/local/nginx/sbin/nginx
```

---

## 🧪 Check Audio and Video Devices

```bash
ls /dev/video*
arecord -l
lsof /dev/snd/*
```

To stop conflicting processes:
```bash
kill -9 <PID>
# Example:
kill -9 4233
```

---

## 📡 FFmpeg Streaming Commands

> Replace `192.168.138.234` with your actual server IP address.

### Simple Video + Audio Stream

```bash
ffmpeg -f v4l2 -framerate 2 -f alsa -i plughw:2,0 \
  -acodec aac -ar 44100 -b:a 128k \
  -f flv rtmp://192.168.138.234:8888/live1/stream
```

### With Resolution and Encoding Settings

```bash
ffmpeg -f v4l2 -framerate 2 -video_size 640x480 -i /dev/video0 \
  -f alsa -i hw:3,0 \
  -vcodec libx264 -preset veryfast -maxrate 300k -bufsize 300k \
  -vf "format=yuv420p" -g 10 -keyint_min 3 \
  -acodec aac -ar 44100 -b:a 128k \
  -f flv rtmp://192.168.138.234:8888/live1/stream
```

### Alternative Stream Path

```bash
ffmpeg -f v4l2 -framerate 2 -video_size 640x480 -i /dev/video0 \
  -f alsa -i hw:3,0 \
  -acodec aac -ar 44100 -b:a 128k \
  -f flv rtmp://192.168.138.234:8888/live/stream
```

---

## ⚙️ Nginx Configuration File

Edit the configuration:
```bash
sudo nano /usr/local/nginx/conf/nginx.conf
```

Reload the server:
```bash
sudo /usr/local/nginx/sbin/nginx -s reload
```

---

## 📂 Permissions for HLS Folder

```bash
sudo chown -R www-data:www-data /tmp/hls
sudo chmod -R 755 /tmp/hls
```

---

## 🧰 Initialization (Recommended on First Use)

```bash
sudo mkdir -p /tmp/hls/live1
sudo mkdir -p /tmp/hls/live2

sudo /usr/local/nginx/sbin/nginx

ffmpeg -f v4l2 -framerate 2 -video_size 640x480 -i /dev/video0 \
  -f alsa -i hw:3,0 \
  -vcodec libx264 -preset veryfast -maxrate 300k -bufsize 300k \
  -vf "format=yuv420p" -g 10 -keyint_min 3 \
  -acodec aac -ar 44100 -b:a 128k \
  -f flv rtmp://192.168.138.234:8888/live1/stream
```

---

## 📎 Notes

- `video0`, `hw:3,0`, and `plughw:2,0` may vary depending on your system — verify with `ls /dev/video*` and `arecord -l`.
- Ensure your Nginx build includes the `ngx_rtmp_module`.

---

Happy streaming! 📺








---

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
