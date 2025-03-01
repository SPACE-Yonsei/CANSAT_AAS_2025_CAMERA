import os
import time
import signal
import sys
import multiprocessing as mp
import cv2
from picamera2 import Picamera2

def capture_and_save_pi(shutdown_event, output_dir="videos", interval=10):
    os.makedirs(output_dir, exist_ok=True)
    try:
        picam2 = Picamera2()
        config = picam2.create_video_configuration(main={"size": (1920, 1080)})
        picam2.configure(config)
        picam2.start()
        print("Raspberry Pi Camera Module 3 started.")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None
        start_time = time.time()

        while not shutdown_event.is_set():
            if out is None or (time.time() - start_time >= interval):
                if out:
                    out.release()
                    print("Raspberry Pi Camera: Video saved.")
                timestamp = int(time.time())
                filename = os.path.join(output_dir, f"pi_camera_{timestamp}.mp4")
                out = cv2.VideoWriter(filename, fourcc, 30.0, (1920, 1080))
                start_time = time.time()

            frame = picam2.capture_array()
            out.write(frame)

    except Exception as e:
        print(f"Error with Raspberry Pi Camera: {e}")
    finally:
        if out:
            out.release()
        picam2.close()
        print("Raspberry Pi Camera stopped.")

def capture_and_save_usb(shutdown_event, usb_index, output_dir="videos", interval=10):
    os.makedirs(output_dir, exist_ok=True)
    try:
        cap = cv2.VideoCapture(usb_index, cv2.CAP_V4L2)
        if not cap.isOpened():
            print(f"USB Camera (index {usb_index}) could not be opened.")
            return
        print(f"USB Camera (index {usb_index}) started.")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None
        start_time = time.time()

        while not shutdown_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print(f"USB Camera (index {usb_index}): Failed to capture frame.")
                break

            if out is None or (time.time() - start_time >= interval):
                if out:
                    out.release()
                    print(f"USB Camera (index {usb_index}): Video saved.")
                timestamp = int(time.time())
                filename = os.path.join(output_dir, f"usb_camera_{usb_index}_{timestamp}.mp4")
                out = cv2.VideoWriter(filename, fourcc, 30.0, (1920, 1080))
                start_time = time.time()

            out.write(frame)

    except Exception as e:
        print(f"Error with USB Camera (index {usb_index}): {e}")
    finally:
        if out:
            out.release()
        if cap:
            cap.release()
        print(f"USB Camera (index {usb_index}) stopped.")

def handle_signal(sig, frame):
    print("Shutdown signal received. Cleaning up...")
    shutdown_event.set()

def main():
    output_dir = "videos" 
    interval = 10   
    usb_index = 10    

    global shutdown_event
    shutdown_event = mp.Event()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    processes = []

    p_pi = mp.Process(target=capture_and_save_pi, args=(shutdown_event, output_dir, interval))
    p_pi.start()
    processes.append(p_pi)

    p_usb = mp.Process(target=capture_and_save_usb, args=(shutdown_event, usb_index, output_dir, interval))
    p_usb.start()
    processes.append(p_usb)

    try:
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
