import os
import time
import signal
import sys
import multiprocessing as mp
import cv2
from picamera2 import Picamera2

def capture_and_save_pi(shutdown_event, output_dir="videos", interval=10):
    """라즈베리파이 카메라 모듈3로 영상을 캡처하여 주기적으로 저장."""
    os.makedirs(output_dir, exist_ok=True)
    try:
        picam2 = Picamera2()  # 기본 Pi 카메라 모듈3 사용
        config = picam2.create_video_configuration(main={"size": (1920, 1080)})
        picam2.configure(config)
        picam2.start()
        print("Raspberry Pi Camera Module 3 started.")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None
        start_time = time.time()

        while not shutdown_event.is_set():
            # 저장 간격이 지나면 새로운 영상 파일 생성
            if out is None or (time.time() - start_time >= interval):
                if out:
                    out.release()
                    print("Raspberry Pi Camera: Video saved.")
                timestamp = int(time.time())
                filename = os.path.join(output_dir, f"pi_camera_{timestamp}.mp4")
                out = cv2.VideoWriter(filename, fourcc, 30.0, (1920, 1080))
                start_time = time.time()

            # Picamera2로 프레임 캡처
            frame = picam2.capture_array()
            out.write(frame)

        # 종료 시 영상 파일 릴리즈
    except Exception as e:
        print(f"Error with Raspberry Pi Camera: {e}")
    finally:
        if out:
            out.release()
        picam2.close()
        print("Raspberry Pi Camera stopped.")

def capture_and_save_usb(shutdown_event, usb_index, output_dir="videos", interval=10):
    """USB 카메라로 영상을 캡처하여 주기적으로 저장."""
    os.makedirs(output_dir, exist_ok=True)
    try:
        # USB 카메라 열기 (V4L2 백엔드 사용)
        cap = cv2.VideoCapture(usb_index, cv2.CAP_V4L2)
        if not cap.isOpened():
            print(f"USB Camera (index {usb_index}) could not be opened.")
            return
        print(f"USB Camera (index {usb_index}) started.")

        # 해상도 설정 (필요 시 조정)
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

            # 저장 간격이 지나면 새로운 영상 파일 생성
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
    output_dir = "videos"    # 영상 저장 디렉토리
    interval = 10            # 영상 파일 저장 간격 (초)
    usb_index = 10           # USB 카메라의 인덱스 (필요에 따라 조정)

    global shutdown_event
    shutdown_event = mp.Event()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    processes = []

    # Raspberry Pi 카메라 모듈3 프로세스 시작
    p_pi = mp.Process(target=capture_and_save_pi, args=(shutdown_event, output_dir, interval))
    p_pi.start()
    processes.append(p_pi)

    # USB 카메라 프로세스 시작
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
