from picamera2 import Picamera2
from datetime import datetime
import time

PICAM_VIDEO_DIR = "PICAM_Video"

# Since there will be multiple files with different timestamp on the name, set the header
PICAM_VIDEO_NAME_HEADER = "PICAM"

# Set the format of video
PICAM_VIDEO_FORMAT = "avi"

# Set the frame rate of video
PICAM_VIDEO_FRAMERATE = int(30)
PICAM_CONV_FRAMERATE = int(1000000/PICAM_VIDEO_FRAMERATE)

# Set the resolution of video
PICAM_VIDEO_WIDTH = int(640)
PICAM_VIDEO_HEIGHT = int(480)

# Create empty pi camera object
picam2 = None

def init_picam():
    global picam2

    picam2 = Picamera2()
    
    video_config = picam2.create_video_configuration(
        main={"size": (PICAM_VIDEO_WIDTH, PICAM_VIDEO_HEIGHT), "format": "MJPEG"},
        controls={"FrameDurationLimits": (PICAM_CONV_FRAMERATE, PICAM_CONV_FRAMERATE)}
    )

    picam2.configure(video_config)

def record_picam(record_time_sec:int):
    global picam2
    
    picam2.start()
    picam2.start_recording(f"{PICAM_VIDEO_DIR}/{PICAM_VIDEO_NAME_HEADER}_{datetime.now():%Y%m%d_%H%M%S}.{PICAM_VIDEO_FORMAT}")
    time.sleep(sec)
    picam2.stop_recording()
    picam2.stop()

if __name__ == "__main__":
    init_picam()
    record_picam(5)

