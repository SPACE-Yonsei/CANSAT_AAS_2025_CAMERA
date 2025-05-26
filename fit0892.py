#!/usr/bin/env python3
from datetime import datetime
import time
import pathlib
import cv2

# ──────────────────────────────────────────────
FIT_VIDEO_DIR         = pathlib.Path("FIT0892_Video")
FIT_VIDEO_NAME_HEADER = "FIT0892"
RECORD_SEC            = 5
FPS                   = 25
WIDTH, HEIGHT         = 640, 480
# ──────────────────────────────────────────────

def init_cam():
    """
    Open the USB camera via V4L2 and prepare MJPG codec.
    Returns (VideoCapture, fourcc) or (None, None) on failure.
    """
    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH,  WIDTH)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cam.set(cv2.CAP_PROP_FPS,         FPS)
    if not cam.isOpened():
        print("Error: cannot open camera index 0")
        return None, None

    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    return cam, fourcc

def record(cam, fourcc, sec: int):
    """
    Record `sec` seconds of video from `cam` into an AVI file.
    """
    # ensure output directory exists
    FIT_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    # timestamped filename
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = FIT_VIDEO_DIR / f"{FIT_VIDEO_NAME_HEADER}_{stamp}.avi"

    print(f"Recording to {out_path} for {sec} seconds @ {FPS} FPS...")
    writer = cv2.VideoWriter(str(out_path), fourcc, FPS, (WIDTH, HEIGHT))
    if not writer.isOpened():
        print("Error: cannot open video writer")
        return

    max_frames = FPS * sec
    for idx in range(max_frames):
        ret, frame = cam.read()
        if not ret:
            print(f"Warning: frame #{idx} capture failed")
            break
        writer.write(frame)
        # optional: sleep to better match real-time FPS
        # time.sleep(1.0 / FPS)

    writer.release()
    print("Recording complete.")

def terminate(cam):
    """
    Release the camera.
    """
    if cam is not None:
        cam.release()
    print("Camera released.")

def main():
    cam, fourcc = init_cam()
    if cam is None or fourcc is None:
        return

    try:
        record(cam, fourcc, RECORD_SEC)
    except KeyboardInterrupt:
        print("Recording interrupted by user.")
    finally:
        terminate(cam)

if __name__ == "__main__":
    main()

