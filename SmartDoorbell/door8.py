#!/usr/bin/python3
# -*- coding: utf-8 -*-
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from PIL import ImageFont  # Import ImageFont for custom fonts
from time import sleep
import time
import threading
import socket
import os
import smbus
import pyaudio
import wave
import math
from gpiozero import Button
from signal import pause  # Use pause to keep the program running
import gpiozero as zgpio
import subprocess
import paho.mqtt.client as mqtt
import logging
import tonghua
import traceback
import sys
import motordoor
from gpiozero import LED

# Server UDP address and port
udp_server_address = ('192.168.211.51', 8699)
# TCP server address and port
tcp_server_address = ('192.168.211.51', 8700)  # Modify to your actual TCP server IP and port
#mqtt addr port reading
mqtt_addr = "192.168.1.115"  
port = 1883  
username = "ha"  
password = "ha" 
# MQTT Configuration Variables sending
MQTT_BROKER = "192.168.1.115"      # Replace with your MQTT broker address
MQTT_PORT = 1883                     # Replace with your MQTT broker port if different
MQTT_USERNAME = None                 # Replace with your MQTT username if required
MQTT_PASSWORD = None                 # Replace with your MQTT password if required
MQTT_TOPIC1 = "/homeassistant/sent/door"
MQTT_TOPIC2 = "/homeassistant/sent/light"

# Initialize the audio player with an RTMP stream URL
audio_player = tonghua.VLCAudioPlayer("rtmp://0.0.0.0:8889/live2/stream")
# Initialize OLED display
__version__ = 1.0
serial = i2c(port=1, address=0x3C)  # Adjust the address according to your OLED module
device = ssd1306(serial)
print("Current version:", __version__)

# Load a larger font (e.g., size 16)
try:
    # Adjust the path to the font file based on your system
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Example for Linux
    # For Windows, it might be: "C:\\Windows\\Fonts\\Arial.ttf"
    # For macOS, it might be: "/Library/Fonts/Arial.ttf"
    large_font = ImageFont.truetype(font_path, 16)  # Font size 16 for double size
except IOError:
    print("Font file not found. Using default font.")
    large_font = ImageFont.load_default()

def oled_display(text_lines):
    """
    Display multiple lines of text on the OLED.
    
    Args:
        text_lines (list of str): List of text lines to display.
    """
    with canvas(device) as draw:
        # Clear the screen
        draw.rectangle(device.bounding_box, outline="black", fill="black")
        # Set text position and style
        for i, line in enumerate(text_lines):
            y = i * 20  # Increased vertical spacing for larger font
            draw.text((0, y), line, font=large_font, fill="white")  # Use the larger font

# Display the initial screen
def display_initial_screen():
    oled_display(["1:Call 2:Open", "3:Rec  4:Bell"])

# Remove LCD-related I2C and smbus initialization
# I2C_ADDR = 0x27  # I2C address for 1602 LCD
# bus = smbus.SMBus(1)

# Remove LCD initialization and writing functions
# def lcd_init():
#     ...
# def lcd_write(cmd, mode=0):
#     ...
# def lcd_toggle_enable(data):
#     ...
# def lcd_display_string(text, line):
#     ...

# Initialize buttons without specifying Pin Factory
button1 = Button(21)
button2 = Button(27)
button3 = Button(22)
button4 = Button(23)

# Recording parameters
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "output1.wav"

# Initialize PyAudio
p = pyaudio.PyAudio()

# Create UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.settimeout(5)  # Set timeout to 5 seconds
udp_socket.bind(('0.0.0.0', 8699))


def publish_mqtt(client, topic, message):
    """
    Publishes a message to a specified MQTT topic.
    
    Args:
        client: The MQTT client instance.
        topic (str): The topic to publish to.
        message (str): The message to publish.
    """
    try:
        message = str(message)
        topic = f"/homeassistant/topic/{topic}"
        result = client.publish(topic, message)
        status = result[0]
        if status == 0:
            logging.info(f"Sent `{message}` to topic `{topic}`")
        else:
            logging.error(f"Failed to send message to topic {topic}")
    except Exception as e:
        logging.error(f"Error publishing to MQTT topic `{topic}`: {e}")
        logging.debug(traceback.format_exc())

# Define a new function to handle OLED display
def oled_display_strings(lines):
    oled_display(lines)

# Display the initial information
display_initial_screen()

# Bind button events
button1.when_pressed = lambda: handle_recording()
button2.when_pressed = lambda: handle_call()
button3.when_pressed = lambda: handle_doorbell()
button4.when_pressed = lambda: handle_open_request()

# Global variables and locks for tracking call status and timers
call_active = False
call_lock = threading.Lock()
call_timer = None
call_lock1 = threading.Lock()
call_lock2 = threading.Lock()
call_lock3 = threading.Lock()
dooropen_lock = threading.Lock()
call_AR = 'NONE'

# Auto hang-up function
def auto_hang_up():
    global call_active, call_timer
    with call_lock:
        if call_active:
            udp_socket.sendto(b'HANG_UP', udp_server_address)
            oled_display_strings(["Call ended (Timeout)", ""])
            call_active = False
            call_timer = None
    sleep(2)
    display_initial_screen()

# Recording functionality
def handle_recording():
    """
    Recording functionality that records audio and saves it to a file,
    with improved error handling and resource management.
    """
    oled_display_strings(["Recording...", ""])

    record_start_time = time.time()

    # Open audio stream
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
    except Exception as e:
        oled_display_strings(["Stream error", ""])
        print(f"Failed to open audio stream: {e}")
        sleep(2)
        display_initial_screen()
        return

    frames = []
    try:
        for i in range(0, int(RATE / CHUNK * 10)):  # 10 seconds of recording
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except Exception as e:
                oled_display_strings(["Recording error", ""])
                print(f"Error during recording: {e}")
                break

    finally:
        # Stop stream and release resources
        stream.stop_stream()
        stream.close()

    # Save recording to file
    try:
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
    except Exception as e:
        oled_display_strings(["Save error", ""])
        print(f"Failed to save audio file: {e}")
        sleep(2)
        display_initial_screen()
        return

    # Recording completed prompt
    oled_display_strings(["Recording ", "done"])
    sleep(1)
    client = mqtt.Client()
    try:
        client.connect(mqtt_addr, port)
        logging.info(f"Connected to MQTT broker at {mqtt_addr}:{port}")
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker at {mqtt_addr}:{port}. Error: {e}")
        logging.debug(traceback.format_exc())
        sys.exit(1)  # Exit if unable to connect to MQTT broker

    publish_mqtt(client, "recording", '1')
    # Send recording file via TCP
    try:
        # Establish TCP connection
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.settimeout(3)
        tcp_socket.connect(tcp_server_address)
        print(f"Connected to TCP server at {tcp_server_address}")

        # Send a fixed-length header 'RECORDING' (9 bytes)
        tcp_socket.sendall(b'RECORDING')  # Ensure exactly 9 bytes

        # Open and send the WAV file
        with open(WAVE_OUTPUT_FILENAME, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                tcp_socket.sendall(data)
        print("WAV file sent successfully via TCP.")
        tcp_socket.close()

        sleep(1)
        publish_mqtt(client, "recording", '0')

    except Exception as e:
        oled_display_strings(["Send error", ""])
        print(f"Failed to send recording file via TCP: {e}")
        sleep(2)
        display_initial_screen()
        return
    publish_mqtt(client, "recording", '0')
    client.disconnect()

    oled_display_strings(["File sent", ""])
    sleep(2)
    display_initial_screen()

in_call_thread = False

def call_thread():
    """Thread to handle call logic"""
    global call_active, in_call_thread

    with call_lock1:
        if not call_active:
            # If the call has been hung up, exit the thread
            in_call_thread = False
            return

        # Send call request
        udp_socket.sendto(b'CALL_REQUEST', udp_server_address)
        oled_display_strings(["Calling...", ""])

        call_start_time = time.time()

        while call_active:
            # Check for timeout
            if time.time() - call_start_time > 10:
                udp_socket.sendto(b'HANG_UP', udp_server_address)
                oled_display_strings(["No answer", ""])
                call_active = False
                sleep(1)
                break

            # Receive response from the device
            try:
                if call_AR == "ACCEPT_CALL":
                    # Start the call
                    oled_display_strings(["Call answered", ""])
                    sleep(1)
                    talking_start_time = time.time()
                    oled_display_strings(["Talking 0s", ""])
                    audio_player.start()
                    # Call timing
                    while call_active:
                        elapsed_time = int(time.time() - talking_start_time)
                        oled_display_strings([f"Talking {elapsed_time}s", ""])
                        sleep(0.1)
                        # Detect hang up
                        try:
                            if call_AR == "HANG_UP":  # Peer hung up
                                call_active = False
                                oled_display_strings(["Call ended by", "peer"])
                                sleep(2)
                                audio_player.stop()
                                break
                        except socket.timeout:
                            continue  # No message received, continue timing
                        except OSError as e:
                            if e.errno == 9:
                                print("Socket has been closed. Exiting thread.")
                                call_active = False
                                break
                            else:
                                raise
                    break

                elif call_AR == "REJECT_CALL":  # Peer rejected
                    # udp_socket.sendto(b'HANG_UP', udp_server_address)
                    oled_display_strings(["Call rejected", ""])
                    call_active = False
                    sleep(1)
                    break

            except socket.timeout:
                continue
            except OSError as e:
                if e.errno == 9:
                    print("Socket has been closed. Exiting thread.")
                    call_active = False
                    break
                else:
                    raise

        # Call ended handling
        oled_display_strings(["Call ended", ""])
        sleep(2)
        display_initial_screen()
        in_call_thread = False  # Mark the thread as finished

def handle_call():
    """Handle button press events for calls"""
    global call_active, in_call_thread

    with call_lock2:
        if not call_active:
            # Start the call
            call_active = True
            if not in_call_thread:
                in_call_thread = True
                threading.Thread(target=call_thread, daemon=True).start()
        else:
            # Hang up the call
            call_active = False
            udp_socket.sendto(b'HANG_UP', udp_server_address)
            audio_player.stop()

# Doorbell functionality
def get_default_sink():
    try:
        output = subprocess.check_output(['pactl', 'get-default-sink']).decode().strip()
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving default sink: {e}")
    return None

def get_volume(sink):
    try:
        output = subprocess.check_output(['pactl', 'get-sink-volume', sink]).decode()
        # Example output: "Volume: front-left: 65536 / 100% / 0.00 dB, front-right: 65536 / 100% / 0.00 dB"
        volumes = [line.split('/')[1].strip() for line in output.splitlines() if '/' in line]
        if volumes:
            # Calculate average volume if multiple channels
            volumes = [int(v.replace('%', '')) for v in volumes]
            average_volume = sum(volumes) // len(volumes)
            return f"{average_volume}%"
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving volume for sink '{sink}': {e}")
    return '100%'  # Default volume if retrieval fails

def set_volume(sink, volume):
    try:
        subprocess.run(['pactl', 'set-sink-volume', sink, volume], check=True)
        print(f"Set {sink} volume to {volume}")
    except subprocess.CalledProcessError as e:
        print(f"Error setting volume for sink '{sink}': {e}")

def handle_doorbell():
    # Display doorbell ringing information
    oled_display_strings(["Doorbell ", "ringing"])
    
    # Get default sink
    default_sink = get_default_sink()
    if not default_sink:
        print("Could not determine default sink. Exiting.")
        return
    
    # Initialize original_volume with a default value
    original_volume = '100%'  # Default to 100% in case retrieval fails
    
    try:
        # Get current volume to restore it later
        original_volume = get_volume(default_sink)
        print(f"Original {default_sink} Volume: {original_volume}")
        
        # Set volume to 50%
        set_volume(default_sink, '50%')
        
        # Play doorbell sound effect
        subprocess.run(['aplay', '/home/link/doorbell/doorbell.wav'], check=True)
        print("Played doorbell sound")
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Restore original volume
        set_volume(default_sink, original_volume)
    sleep(2)
    display_initial_screen()

# Open door request
def handle_open_request():
    udp_socket.sendto(b'OPEN_DOOR_REQUEST', udp_server_address)
    oled_display_strings(["Open request has", "been sent"])
    sleep(2)
    display_initial_screen()

# 在全局范围内初始化 led2
led2 = LED(16)  # 使用 BCM 模式的 GPIO 16

def listen_for_open_command():
    """
    Listens for door open commands via UDP and MQTT.
    """
    global call_AR
    with dooropen_lock:
        # Setup MQTT Client
        mqtt_client = mqtt.Client()

        if MQTT_USERNAME and MQTT_PASSWORD:
            mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                client.subscribe(MQTT_TOPIC1)
                print(f"Subscribed to MQTT topic: {MQTT_TOPIC1}")
                client.subscribe(MQTT_TOPIC2)
                print(f"Subscribed to MQTT topic: {MQTT_TOPIC2}")
            else:
                print(f"Failed to connect to MQTT Broker, return code {rc}")

        def on_message(client, userdata, msg):
            try:
                payload = msg.payload.decode().strip()
                print(f"Received MQTT message {payload} on topic {msg.topic}")
                
                # 处理 MQTT_TOPIC1 的消息
                if msg.topic == MQTT_TOPIC1 and payload == "1":
                    # 执行开门操作
                    oled_display_strings(["Door is open", ""])
                    led = LED(13)  # 使用局部变量 led
                    led.on()
                    sleep(2)
                    display_initial_screen()
                    led.close()
                    # 发布 '0' 表示操作完成
                    client.publish(MQTT_TOPIC1, "0")
                    print(f"Published '0' to MQTT topic {MQTT_TOPIC1} to indicate completion.")
                
                # 处理 MQTT_TOPIC2 的消息
                if msg.topic == MQTT_TOPIC2:
                    if payload == "1":  # 如果收到 "1"，点亮 led2
                        led2.on()
                        print("LED2 is ON")
                    elif payload == "0":  # 如果收到 "0"，关闭 led2
                        led2.off()
                        print("LED2 is OFF")
                    else:
                        print(f"Ignored invalid payload for MQTT_TOPIC2: {payload}")

            except Exception as e:
                print(f"Error processing MQTT message: {e}")

        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        except Exception as e:
            print(f"Unable to connect to MQTT Broker: {e}")
            return

        # Start MQTT loop in a separate thread
        mqtt_client.loop_start()

        try:
            while True:
                try:
                    data, _ = udp_socket.recvfrom(1024)
                    if data == b'HANG_UP' or data == b'REJECT_CALL':
                        call_AR = 'HANG_UP'
                        print(call_AR)
                    elif data == b'ACCEPT_CALL':
                        call_AR = 'ACCEPT_CALL'
                        print(call_AR)
                    elif data == b'OPEN_DOOR':
                        servo_motor = ServoMotor(gpio_pin=13)
                        servo_motor.set_angle(90)  # 开门
                        oled_display_strings(["Door is open", ""])
                        sleep(2)
                        print('door opened')
                        display_initial_screen()
                        servo_motor.set_angle(180)  # 关门
                except socket.timeout:
                    continue  # Continue waiting on timeout
                except TimeoutError:
                    continue  # Handle timeout errors
                except OSError as e:
                    if e.errno == 9:
                        print("Socket has been closed. Exiting thread.")
                        break
                    else:
                        raise
        except KeyboardInterrupt:
            print("Interrupted by user. Shutting down.")
        finally:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print("Cleaned up MQTT connections.")

# Start listening for door open commands in a separate thread
threading.Thread(target=listen_for_open_command, daemon=True).start()

# Use pause to keep the program running and allow gpiozero to handle events
try:
    pause()
except KeyboardInterrupt:
    if call_timer is not None:
        call_timer.cancel()
    udp_socket.close()
    p.terminate()
