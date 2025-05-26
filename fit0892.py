from datetime import datetime
import os
import cv2

# Camera index (0 for the first camera)
FIT0892_CAMERA_INDEX = 0
# Directory to save videos
FIT0892_VIDEO_DIR = "FIT0892_Video"
# Filename header
FIT0892_VIDEO_NAME_HEADER = "FIT0892"
# Video settings
FIT0892_VIDEO_FORMAT = "avi"
FIT0892_VIDEO_FRAMERATE = 25
FIT0892_VIDEO_WIDTH = 640
FIT0892_VIDEO_HEIGHT = 480

# VideoWriter handle
out = None

def init_fit0892():
    """
    Initialize the camera and prepare video codec.
    Returns (VideoCapture, fourcc) on success, (None, None) on failure.
    """
    # Ensure output directory exists
    os.makedirs(FIT0892_VIDEO_DIR, exist_ok=True)

    # Open camera
    cam = cv2.VideoCapture(FIT0892_CAMERA_INDEX)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, FIT0892_VIDEO_WIDTH)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, FIT0892_VIDEO_HEIGHT)
    cam.set(cv2.CAP_PROP_FPS, FIT0892_VIDEO_FRAMERATE)

    if not cam.isOpened():
        print("Error: Could not open camera index", FIT0892_CAMERA_INDEX)
        return None, None

    # MJPG codec
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    return cam, fourcc


def record_fit0892(cam, fourcc, record_time_sec: int):
    """
    Record a video from 'cam' for 'record_time_sec' seconds using 'fourcc'.
    """
    global out
    if cam is None or fourcc is None:
        print("Error: Camera or codec not initialized.")
        return

    # Calculate frame count
    max_frames = int(FIT0892_VIDEO_FRAMERATE * record_time_sec)
    # Safe filename timestamp (no colons)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    video_path = os.path.join(
        FIT0892_VIDEO_DIR,
        f"{FIT0892_VIDEO_NAME_HEADER}_{timestamp}.{FIT0892_VIDEO_FORMAT}"
    )

    out = cv2.VideoWriter(
        video_path,
        fourcc,
        FIT0892_VIDEO_FRAMERATE,
        (FIT0892_VIDEO_WIDTH, FIT0892_VIDEO_HEIGHT)
    )

    if not out.isOpened():
        print("Error: Could not open video writer.")
        return

    frame_count = 0
    while frame_count < max_frames:
        ret, frame = cam.read()
        if not ret:
            print("Warning: Frame capture failed at count", frame_count)
            break
        out.write(frame)
        print(f"Writing frame {frame_count + 1}/{max_frames}")
        frame_count += 1

    out.release()
    print(f"Recording complete: {video_path}")


def terminate_fit0892(cam):
    """
    Release camera and any open writer.
    """
    global out
    if cam is not None:
        cam.release()
    if out is not None:
        out.release()
    print("Camera and writer released.")


def main():
    cam, fourcc = init_fit0892()
    if cam is None:
        return
    # Record 5 seconds (adjust as needed)
    record_time_sec = 5
    record_fit0892(cam, fourcc, record_time_sec)
    terminate_fit0892(cam)

if __name__ == "__main__":
    main()
