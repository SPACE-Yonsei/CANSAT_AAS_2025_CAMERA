from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
import time


# zero2에 csi 하나 돌리는 코드입니다

# Picamera2 객체 생성
picam2 = Picamera2()

# MJPEG 코덱과 640x480 해상도로 영상 녹화용 설정 생성
# video_config = picam2.create_video_configuration({
#     "size": (640, 480),
#     "format": "YUV420"
# })
picam2.sensor_mode = 2
picam2.framerate = 15 / 1
picam2.resolution = (640, 480)
# picam2.configure(video_config)

# 카메라 시작 및 안정화 시간 대기
picam2.start()
time.sleep(2)  # 카메라가 안정화될 시간을 줍니다.

# 녹화 시작 (파일 확장자는 mjpeg로 저장)
encoder = MJPEGEncoder()
picam2.start_recording(encoder, "recorded_video.mjpeg")
print("영상 녹화 시작...")
