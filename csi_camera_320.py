from picamera2 import Picamera2
import time

# Picamera2 객체 생성
picam2 = Picamera2()

# 영상 녹화를 위한 설정 생성 및 적용
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

# 카메라 시작 및 안정화 시간 대기
picam2.start()
time.sleep(2)  # 카메라가 안정화될 시간을 줍니다.

# 녹화 시작 (녹화 파일: recorded_video.h264)
picam2.start_recording("recorded_video.h264")
print("영상 녹화 시작...")

# 10초간 녹화
time.sleep(10)

# 녹화 중지
picam2.stop_recording()
print("영상 녹화 종료, 파일 저장 완료.")

# 카메라 종료
picam2.stop()
