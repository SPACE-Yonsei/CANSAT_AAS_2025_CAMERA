import subprocess
import time

def record_segmented():
    cmd = [
        'ffmpeg',
        '-f', 'v4l2',
        '-input_format', 'mjpeg',      # Match camera's hardware format
        '-video_size', f'{640}xP{480}',      # From your v4l2-ctl output
        '-framerate', '25',            # As per camera specs
        '-i', '/dev/video2',           # Your camera device
        '-c:v', 'copy',                # No re-encoding
        '-f', 'segment',               # Enable segmentation
        '-segment_time', '7',          # 7-second chunks
        '-reset_timestamps', '1',      # Restart timestamps per segment
        'output_%03d.avi'              # Output pattern
    ]
    
    process = subprocess.Popen(cmd)
    
    try:
        while True:
            # Keep running until interrupted
            time.sleep(1)
    except KeyboardInterrupt:
        process.terminate()
        process.wait()

if __name__ == '__main__':
    record_segmented()
