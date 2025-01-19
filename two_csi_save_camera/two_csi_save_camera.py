from picamera2 import Picamera2
import multiprocessing as mp
import os
import time
import signal
import cv2
import sys

def capture_and_save(camera_index, shutdown_event, output_dir="videos", interval=10):
    """주기적으로 영상을 저장하며 두 카메라를 동시 관리."""
    os.makedirs(output_dir, exist_ok=True)

    try:
        picam2 = Picamera2(camera_index)
        picam2.configure(picam2.create_video_configuration(main={"size": (1920, 1080)}))
        picam2.start()
        print(f"Camera {camera_index} started.")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None
        start_time = time.time()

        while not shutdown_event.is_set():
            if out is None or time.time() - start_time >= interval:
                if out:
                    out.release()
                    print(f"Camera {camera_index}: Video saved.")

                timestamp = int(time.time())
                filename = os.path.join(output_dir, f"camera_{camera_index}_{timestamp}.mp4")
                out = cv2.VideoWriter(filename, fourcc, 30.0, (1920, 1080))
                start_time = time.time()

            frame = picam2.capture_array()
            out.write(frame)

    except Exception as e:
        print(f"Error with camera {camera_index}: {e}")
    finally:
        if out:
            out.release()
        picam2.close()
        print(f"Camera {camera_index} stopped.")

def handle_signal(sig, frame):
    print("Shutdown signal received. Cleaning up...")
    shutdown_event.set()

def main():
    camera_indices = [0, 1]  # 사용할 카메라 인덱스
    output_dir = "videos"  # 저장할 디렉토리
    interval = 10  # 저장 간격 (초)

    global shutdown_event
    shutdown_event = mp.Event()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    processes = []

    try:
        for camera_index in camera_indices:
            p = mp.Process(target=capture_and_save, args=(camera_index, shutdown_event, output_dir, interval))
            p.start()
            processes.append(p)

        while not shutdown_event.is_set():
            time.sleep(1)

    finally:
        print("Shutting down all processes.")
        shutdown_event.set()
        for p in processes:
            if p.is_alive():
                p.terminate()
        for p in processes:
            p.join()
        sys.exit(0)

if __name__ == "__main__":
    main()
