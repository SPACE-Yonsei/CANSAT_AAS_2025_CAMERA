#!/usr/bin/env python3
from datetime import datetime
import time
import pathlib
import subprocess
import os

# ──────────────────────────────────────────────
FIT_VIDEO_DIR         = pathlib.Path("FIT0892_Video")
FIT_VIDEO_NAME_HEADER = "F"
FIT_VIDEO_INDEX       = 2
RECORD_SEC            = 7
FPS                   = 25
WIDTH, HEIGHT         = 640,480
# ──────────────────────────────────────────────

log_dir = './cameralog'
if not os.path.exists(log_dir): 
    os.makedirs(log_dir)

fit0892log = open(os.path.join(log_dir, 'fit0892.txt'), 'a')

fit0892_instance : subprocess.Popen = None

def fit0892_start_recording_process(sec: int):

    global fit0892_instance

    if fit0892_instance is not None:
        if fit0892_instance.poll() is None:
            logdata("Process already open! Please Terminate before reopening")
            return

    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    # Make the directory
    FIT_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        'ffmpeg',
        '-nostdin',
        '-f', 'v4l2',
        '-input_format', 'mjpeg',      # Match camera's hardware format
        '-video_size', f'{WIDTH}x{HEIGHT}',      # From your v4l2-ctl output
        '-framerate', f'{FPS}',            # FPS
        '-i', f'/dev/video{FIT_VIDEO_INDEX}',           # Adjust camera index
        '-c:v', 'copy',                # No re-encoding
        '-f', 'segment',               # Enable segmentation
        '-segment_time', f'{sec}',          # segment length
        '-reset_timestamps', '1',      # Restart timestamps per segment
        f'{FIT_VIDEO_DIR}/{FIT_VIDEO_NAME_HEADER}_{timestamp}_%03d.avi' # output file name
    ]

    fit0892_instance = subprocess.Popen(cmd, stdout=fit0892log, stderr=fit0892log)

    return
    
def fit0892_terminate_recording_process():

    global fit0892_instance
    # poll() returns None when process is running
    # check the process has terminated
    if fit0892_instance.poll() is not None:
        logdata("Error when terminating fit0892 : Process already terminated!")
        return
    
    fit0892_instance.terminate()
    fit0892_instance.wait()
    logdata("Terminated fit0892 instance")

    return

def logdata(data_to_log:str):
    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    fit0892log.write(f"[{timestamp}] {data_to_log}")

def main():

    try:
        fit0892_start_recording_process(RECORD_SEC)
        while True:
            time.sleep(5)
            fit0892_start_recording_process(RECORD_SEC)
    except KeyboardInterrupt:
        print("Recording interrupted by user.")
    finally:
        fit0892_terminate_recording_process()

if __name__ == "__main__":
    main()
