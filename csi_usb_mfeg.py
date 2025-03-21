import os
import time
import signal
import sys
import multiprocessing as mp
from picamera2 import Picamera2  # 라즈베리파이 카메라 모듈3 제어용 라이브러리
from picamera2.encoders import MJPEGEncoder
import cv2


def capture_and_save_pi(shutdown_event, output_dir="videos", interval=10):
    os.makedirs(output_dir, exist_ok=True)

    try:
        picam2 = Picamera2()

        picam2.sensor_mode = 2
        picam2.framerate = 15 / 1
        picam2.resolution = (640, 480)

        picam2.start()
        print("Raspberry Pi Camera Module 3 started.")

        while not shutdown_event.is_set():
            timestamp = int(time.time())
            filename = os.path.join(output_dir, f"pi_camera_{timestamp}.mjpeg")

            print(f"녹화 시작: {filename}")
            encoder = MJPEGEncoder()
            picam2.start_recording(encoder, filename)

            time.sleep(interval)

            picam2.stop_recording()
            print("녹화 저장 완료")

    except Exception as e:
        print(f"Error with Raspberry Pi Camera: {e}")

    finally:
        try:
            picam2.stop_recording()
        except:
            pass
        print("Raspberry Pi Camera stopped.")
      
def capture_and_save_usb(shutdown_event, output_dir="videos", interval=10):
    cap = cv2.VideoCapture(index)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 0번 카메라(기본 USB 카메라) 열기
        cap = cv2.VideoCapture(0)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)

        if not cap.isOpened():
            raise Exception("USB 카메라를 열 수 없습니다.")

        print("USB 카메라(FIT0729) 시작됨")

        while not shutdown_event.is_set():
            timestamp = int(time.time())
            filename = os.path.join(output_dir, f"usb_camera_{timestamp}.avi")

            print(f"녹화 시작: {filename}")
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MJPEG 포맷
            out = cv2.VideoWriter(filename, fourcc, 15.0, (640, 480))

            start_time = time.time()
            while time.time() - start_time < interval and not shutdown_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    print("프레임을 읽지 못했습니다.")
                    break
                out.write(frame)

            out.release()
            print("녹화 저장 완료")

    except Exception as e:
        print(f"Error with USB Camera: {e}")

    finally:
        if cap:
            cap.release()
        print("USB 카메라 종료됨")
# -------------------------------------------------------------------------
# 함수: handle_signal
# 목적: SIGINT 또는 SIGTERM 종료 신호를 처리하여 shutdown_event를 설정,
#       모든 프로세스에게 종료 신호를 전달합니다.
# -------------------------------------------------------------------------
def handle_signal(sig, frame):
    print("Shutdown signal received. Cleaning up...")
    shutdown_event.set()

# -------------------------------------------------------------------------
# 메인 함수: 두 카메라를 각각 별도의 프로세스로 실행합니다.
# -------------------------------------------------------------------------
def main():
    output_dir = "videos"    # 저장할 영상 파일들이 위치할 디렉토리 이름
    interval = 10            # 영상 파일 저장 간격 (초)
    usb_index = 10           # USB 카메라의 인덱스 번호 (시스템 환경에 따라 변경 가능)

    global shutdown_event
    shutdown_event = mp.Event()  # 종료 이벤트 객체: 신호 발생 시 True로 설정됨

    # SIGINT(예: Ctrl+C)와 SIGTERM 신호에 대해 handle_signal 함수를 등록합니다.
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    processes = []  # 자식 프로세스들을 저장할 리스트

    # Raspberry Pi Camera Module 3용 프로세스 생성 및 시작
    print("starting save pi")
    p_pi = mp.Process(target=capture_and_save_pi, args=(shutdown_event, output_dir, interval))
    p_pi.start()
    processes.append(p_pi)

    # USB 카메라용 프로세스 생성 및 시작
    p_usb = mp.Process(target=capture_and_save_usb, args=(shutdown_event, usb_index, output_dir, interval))
    #p_usb.start()
    #processes.append(p_usb)

    try:
        # 종료 이벤트가 발생할 때까지 메인 프로세스는 대기합니다.
        while not shutdown_event.is_set():
            time.sleep(1)
    finally:
        print("Shutting down all processes.")
        shutdown_event.set()  # 종료 이벤트를 설정하여 자식 프로세스들에게 종료를 알림
        # 모든 프로세스가 정상 종료되도록 처리합니다.
        for p in processes:
            if p.is_alive():
                p.terminate()
        for p in processes:
            p.join()
        sys.exit(0)

# 스크립트가 직접 실행될 때 메인 함수 호출
if __name__ == "__main__":
    main()
