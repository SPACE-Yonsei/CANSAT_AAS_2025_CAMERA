from picamera2 import Picamera2
import multiprocessing as mp
import os
import time
import signal
import sys

shutdown_event = mp.Event()

def capture_and_save(camera_index, shutdown_event, output_dir="videos"):
    """Capture video from the camera and save to a file."""
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"camera_{camera_index}_{int(time.time())}.mp4")

    try:
        picam2 = Picamera2(camera_index)
        picam2.configure(picam2.create_video_configuration(main={"size": (1920, 1080)}))
        picam2.start()
        print(f"Camera {camera_index} started.")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, 30.0, (1920, 1080))

        while not shutdown_event.is_set():
            frame = picam2.capture_array()
            out.write(frame)

    except Exception as e:
        print(f"Error with camera {camera_index}: {e}")
    finally:
        picam2.close()
        out.release()
        print(f"Camera {camera_index} stopped. Video saved: {filename}")

def handle_signal(sig, frame):
    print("Shutdown signal received. Cleaning up...")
    shutdown_event.set()

def main():
    camera_indices = [0, 1]

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    processes = []

    try:
        for camera_index in camera_indices:
            p = mp.Process(target=capture_and_save, args=(camera_index, shutdown_event))
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
        sys.exit(0)

if __name__ == "__main__":
    main()
