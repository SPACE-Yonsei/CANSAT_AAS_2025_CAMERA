from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
import time

picam2 = Picamera2()

picam2.sensor_mode = 2
picam2.framerate = 15 / 1
picam2.resolution = (640, 480)

picam2.start()
time.sleep(2) 

encoder = MJPEGEncoder()
picam2.start_recording(encoder, "recorded_video.mjpeg")
print("영상 녹화 시작...")

time.sleep(10)
picam2.stop_recording()
