import cv2
import numpy as np
import time
import threading
from queue import Queue
import smbus
import time
import paho.mqtt.client as mqtt
# MQTT Setup
mqtt_addr = "192.168.1.115"  
port = 1883  

class FaceRecognizer:
    def __init__(self, face_cascade_path, model_path, whitelist_path, blacklist_path, frame_interval=1):
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(model_path)
        self.names = ['link','teddy' ]
        self.load_names(whitelist_path, blacklist_path)
        
        self.cap = cv2.VideoCapture('rtmp://192.168.1.115:8888/live1/stream')  # Replace with the correct stream URL
        self.cap.set(3, 640)  # Width
        self.cap.set(4, 480)  # Height

        self.frame_queue = Queue()
        self.last_name = None
        self.last_time = time.time()
        self.detection_pause = 0
        self.same_count = 0
        self.stranger_start_time = None

        # Frame processing interval (every 'frame_interval' frames)
        self.frame_interval = frame_interval
        self.frame_count = 0  # Initialize frame count

    def load_names(self, whitelist_path, blacklist_path):
        """Load names from whitelist and blacklist files."""
        with open(whitelist_path, 'r') as f:
            self.whitelist = set(line.strip() for line in f.readlines())
        with open(blacklist_path, 'r') as f:
            self.blacklist = set(line.strip() for line in f.readlines())

    def capture_frames(self):
        """Capture frames from the video source."""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            self.frame_count += 1  # Increment frame counter

            # Only process every 'frame_interval' frame (e.g., every 15th frame)
            if self.frame_count % self.frame_interval == 0:
                self.frame_queue.put(frame)

    def process_frames(self):
        """Process frames and perform face recognition."""
        while True:
            if self.frame_queue.empty():
                time.sleep(0.01)
                continue

            frame = self.frame_queue.get()

            if self.detection_pause > 0:
                self.detection_pause -= 1
                cv2.imshow('Recognizer', frame)
                if cv2.waitKey(10) & 0xFF == 27:
                    break
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=3, minSize=(100, 100))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                id, confidence = self.recognizer.predict(gray[y:y+h, x:x+w])

                if confidence < 70 and id < len(self.names):
                    name = self.names[id]
                    confidence_text = f"{round(100 - confidence)}%"
                else:
                    name = "unknown"
                    confidence_text = f"{round(100 - confidence)}%"

                cv2.putText(frame, f"{name} {confidence_text}", (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                current_time = time.time()
                if name == "unknown":
                    print('Stranger appears')
                    if self.stranger_start_time is None:
                        self.stranger_start_time = current_time
                    elif current_time - self.stranger_start_time >= 10:
                        cv2.imwrite(f'stranger_{int(current_time)}.jpg', frame[y:y+h, x:x+w])
                        self.stranger_start_time = None
                else:
                    self.stranger_start_time = None

                if name == self.last_name:
                    self.same_count += 1
                    if self.same_count >= 4:
                        self.detection_pause = 100
                        self.same_count = 0
                        print('Sleeping')
                else:
                    self.same_count = 0

                if name != self.last_name or current_time - self.last_time >= 0.5:
                    print(f"Detected: {name} ({confidence_text})")
                    is_whitelisted = name in self.whitelist
                    is_blacklisted = name in self.blacklist
                    print(f"Whitelisted: {is_whitelisted}, Blacklisted: {is_blacklisted}")
                    self.last_name = name
                    self.last_time = current_time
                    self.detection_pause = 10

            cv2.imshow('Recognizer', frame)

            if cv2.waitKey(10) & 0xFF == 27:
                break

    def run(self):
        """Start the threads for capturing and processing frames."""
        capture_thread = threading.Thread(target=self.capture_frames)
        process_thread = threading.Thread(target=self.process_frames)

        capture_thread.start()
        process_thread.start()

        capture_thread.join()
        process_thread.join()

        self.cap.release()
        cv2.destroyAllWindows()


# Example usage
face_recognizer = FaceRecognizer(
    '/home/link/facedetect/haarcascade_frontalface_default.xml',
    'trainer/trainer.yml',
    'whitelist.txt',
    'blacklist.txt'
)
face_recognizer.run()
