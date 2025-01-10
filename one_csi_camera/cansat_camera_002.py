import os
from picamera import PiCamera
from time import sleep
import datetime

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.start_preview()

start_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
base_dir = f'/home/pi/videos/session_{start_time}'
os.makedirs(base_dir, exist_ok=True)

filename = f'{base_dir}/video_{start_time}.h264'
camera.start_recording(filename)

try:
    while True:
        sleep(1)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        new_filename = f'{base_dir}/video_{timestamp}.h264'
        camera.split_recording(new_filename)
        print(f'Saved {new_filename}')
except KeyboardInterrupt:
    print("Recording stopped")
finally:
    camera.stop_recording()
    camera.stop_preview()
    camera.close()
