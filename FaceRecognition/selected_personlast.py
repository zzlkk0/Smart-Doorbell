import cv2
import numpy as np
import time
import threading
from queue import Queue, Empty
import smbus
import paho.mqtt.client as mqtt

# MQTT Setup
mqtt_addr = "192.168.138.234"  
port = 1883  

class FaceRecognizer:
    def __init__(self, face_cascade_path, model_path, whitelist_path, blacklist_path):
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(model_path)
        self.names = ['link', 'teddy']
        self.load_names(whitelist_path, blacklist_path)
        
        self.cap = cv2.VideoCapture('rtmp://192.168.138.234:8888/live1/stream')  # Replace with the correct stream URL
        self.cap.set(3, 640)  # Width
        self.cap.set(4, 480)  # Height

        self.frame_queue = Queue()
        self.names_queue = Queue()
        self.lock = threading.Lock()
        self.last_frame = None
        self.last_unknown_face = None  # To store the face region of the last unknown detection
        self.last_stranger_save_time = 0  # Time when the last stranger photo was saved

        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(mqtt_addr, port, 60)
        self.mqtt_client.loop_start()  # Start the MQTT client loop

        # Timing for frame processing
        self.last_processed_time = 0
        self.processing_interval = 1  # Process every 1 seconds

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
            # Always update the last frame for potential screenshots
            with self.lock:
                self.last_frame = frame.copy()
            # Put the frame into the queue
            self.frame_queue.put(frame)
            # Sleep briefly to limit CPU usage
            time.sleep(0.01)

    def process_frames(self):
        """Process frames and perform face recognition every 0.25 seconds without displaying the video."""
        while True:
            try:
                frame = self.frame_queue.get(timeout=0.1)
            except Empty:
                continue

            current_time = time.time()
            if current_time - self.last_processed_time >= self.processing_interval:
                # Perform face recognition
                self.last_processed_time = current_time

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.15, minNeighbors=3, minSize=(100, 100)
                )

                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    id, confidence = self.recognizer.predict(roi_gray)

                    if confidence < 70 and id < len(self.names):
                        name = self.names[id]
                    else:
                        name = "unknown"

                    confidence_text = f"{round(100 - confidence)}%"
                    print(f"Detected: {name} ({confidence_text})")
                    is_whitelisted = name in self.whitelist
                    is_blacklisted = name in self.blacklist
                    print(f"Whitelisted: {is_whitelisted}, Blacklisted: {is_blacklisted}")

                    # Put the name into the queue for counting
                    self.names_queue.put(name)

                    # If the detected face is unknown, store the face region
                    if name == "unknown":
                        with self.lock:
                            self.last_unknown_face = frame[y:y+h, x:x+w].copy()


    def count_names(self):
        """Count names over a 10-second interval and decide on actions."""
        while True:
            counts = {}
            start_time = time.time()
            while time.time() - start_time < 10:
                try:
                    remaining_time = 10 - (time.time() - start_time)
                    if remaining_time <= 0:
                        break
                    name = self.names_queue.get(timeout=remaining_time)
                    counts[name] = counts.get(name, 0) + 1
                except Empty:
                    pass
            total_counts = sum(counts.values())
            if total_counts == 0:
                self.mqtt_client.publish('/homeassistant/topic/person', "no person")
                continue

            # Check if 'unknown' exceeds threshold
            if counts.get('unknown', 0) > total_counts / 4:
                # Stranger detected
                print("Stranger detected")
                current_time = time.time()
                if current_time - self.last_stranger_save_time >= 30:
                    with self.lock:
                        if self.last_unknown_face is not None:
                            cv2.imwrite(f'/home/link/facedetect/stranger/stranger_{int(current_time)}.jpg', self.last_unknown_face)
                    self.last_stranger_save_time = current_time  # Update last save time
                else:
                    print("Stranger photo already saved recently, skipping save")
                # Continue MQTT messaging
                self.mqtt_client.publish('/homeassistant/topic/person', 'stranger')
            else:
                # Check for known names exceeding threshold
                detected = False
                for name, count in counts.items():
                    if name != 'unknown' and count > total_counts / 4:
                        print(f"Person detected: {name}")
                        # Send via MQTT
                        self.mqtt_client.publish('/homeassistant/topic/person', name)
                        detected = True
                        break
                if not detected:
                    # No person detected sufficiently
                    print("No person detected")
                    # Send "no person" via MQTT
                    self.mqtt_client.publish('/homeassistant/topic/person', "no person")

            # Short sleep before next interval
            time.sleep(0.01)

    def run(self):
        """Start the threads for capturing and processing frames."""
        capture_thread = threading.Thread(target=self.capture_frames)
        process_thread = threading.Thread(target=self.process_frames)
        counting_thread = threading.Thread(target=self.count_names)
        counting_thread.daemon = True

        capture_thread.start()
        process_thread.start()
        counting_thread.start()

        capture_thread.join()
        process_thread.join()

        self.cap.release()
        cv2.destroyAllWindows()
        self.mqtt_client.loop_stop()  # Stop the MQTT client loop

# Example usage
face_recognizer = FaceRecognizer(
    '/home/link/facedetect/haarcascade_frontalface_default.xml',
    'trainer/trainer.yml',
    'whitelist.txt',
    'blacklist.txt'
)
face_recognizer.run()
