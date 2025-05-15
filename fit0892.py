import cv2
from datetime import datetime
import os

# Usually the index of camera is 0 when only one camera is connected to USB port
FIT0892_CAMERA_INDEX = 0

# Directory name where the video is saved
FIT0892_VIDEO_DIR = "FIT0892_Video"

# Since there will be multiple files with different timestamp on the name, set the header
FIT0892_VIDEO_NAME_HEADER = "FIT0892"

# Set the format of video
FIT0892_VIDEO_FORMAT = "avi"

# Set the frame rate of video
FIT0892_VIDEO_FRAMERATE = int(25)

# Set the resolution of video
FIT0892_VIDEO_WIDTH = int(640)
FIT0892_VIDEO_HEIGHT = int(480)

# Create empty video output variable
out = None

def init_fit0892():

    # Create directory for video if it doesn't exist
    os.makedirs(FIT0892_VIDEO_DIR, exist_ok=True)

    # Set the index of camera
    cam = cv2.VideoCapture(FIT0892_CAMERA_INDEX)

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, FIT0892_VIDEO_WIDTH)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, FIT0892_VIDEO_HEIGHT)
    cam.set(cv2.CAP_PROP_FPS, FIT0892_VIDEO_FRAMERATE)

    if not cam.isOpened():
        return False
    
    # Set fourcc variable
    fourcc = cv2.VideoWriter.fourcc('M','J','P','G')

    return cam, fourcc

def record_fit0892(cam, fourcc, record_time_sec : int):
    global out

    # Count the frames wrote to file
    current_frame_count = 0

    # The max frame count is determined by multiplying the framerate and recording second
    # e.g) record 3 second video with 30fps -> record 90 frames
    max_frame_count = FIT0892_VIDEO_FRAMERATE * record_time_sec

    # Set timestemp
    timestamp = datetime.now().isoformat(sep=':', timespec='milliseconds')

    # Set video file path
    video_path = f"{FIT0892_VIDEO_DIR}/{FIT0892_VIDEO_NAME_HEADER}_{timestamp}.{FIT0892_VIDEO_FORMAT}"

    out = cv2.VideoWriter(video_path, fourcc, FIT0892_VIDEO_FRAMERATE, (FIT0892_VIDEO_WIDTH, FIT0892_VIDEO_HEIGHT))

    while current_frame_count < max_frame_count:
        ret, frame = cam.read()

        if not ret:
            print("Error writing frame")
            continue

        out.write(frame)
        print(f"writing frame {current_frame_count}")
        # only increment frame counter on successful frame read
        current_frame_count += 1

    out.release()

# Camera Termination Method
def terminate_fit0892(cam):
    global out

    cam.release()
    out.release()

if __name__ == "__main__": 
    init_fit0892()
    record_fit0892(5)
    terminate_fit0892()