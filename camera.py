import os
import time
import signal
import sys
import multiprocessing as mp
#import cv2 # USB 카메라용
from picamera2 import Picamera2  # 라즈베리파이 카메라 모듈3 제어용 라이브러리

# -------------------------------------------------------------------------
# 함수: capture_and_save_pi
# 목적: Raspberry Pi Camera Module 3를 사용하여 영상을 캡처하고,
#       일정 시간 간격마다 (interval) 캡처한 영상을 MP4 파일로 저장합니다.
# -------------------------------------------------------------------------
def capture_and_save_pi(shutdown_event, output_dir="videos", interval=10):
    # 영상 파일을 저장할 디렉토리가 존재하지 않으면 생성합니다.
    os.makedirs(output_dir, exist_ok=True)
    try:
        print("camera out")
        # Picamera2 객체를 생성하여 라즈베리파이 카메라 모듈3에 접근합니다.
        picam2 = Picamera2()
        # 1920x1080 해상도로 영상 캡처를 위한 기본 구성(configuration)을 생성합니다.
        config = picam2.create_video_configuration(main={"size": (1920, 1080)})
        # 구성 설정을 적용합니다.
        picam2.configure(config)
        # 카메라 스트림을 시작합니다.
        picam2.start()
        print("Raspberry Pi Camera Module 3 started.")

        # OpenCV의 VideoWriter를 위한 코덱 설정 (여기서는 'mp4v' 사용)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None  # 영상 저장을 위한 VideoWriter 객체를 초기화합니다.
        start_time = time.time()  # 현재 시간을 저장하여 저장 주기를 측정합니다.

        # shutdown_event가 발생할 때까지 반복합니다.
        while not shutdown_event.is_set():
            # 지정한 간격(interval)마다 새 파일로 영상을 저장합니다.
            if out is None or (time.time() - start_time >= interval):
                if out:
                    # 이전에 생성된 파일을 닫습니다.
                    out.release()
                    print("Raspberry Pi Camera: Video saved.")
                # 현재 시간을 기반으로 파일명을 생성 (타임스탬프 사용)
                timestamp = int(time.time())
                filename = os.path.join(output_dir, f"pi_camera_{timestamp}.mp4")
                # VideoWriter 객체 생성: 파일명, 코덱, FPS(30fps), 해상도 설정
                out = cv2.VideoWriter(filename, fourcc, 30.0, (1920, 1080))
                # 새로운 저장 주기를 시작합니다.
                start_time = time.time()

            # Picamera2를 사용하여 현재 프레임을 캡처합니다.
            frame = picam2.capture_array()
            # 캡처한 프레임을 VideoWriter를 통해 파일에 기록합니다.
            out.write(frame)

    except Exception as e:
        print(f"Error with Raspberry Pi Camera: {e}")
    finally:
        # 예외 발생 여부와 상관없이 마지막에 열려있는 영상 파일을 닫습니다.
        if out:
            out.release()
        # 카메라 장치를 해제합니다.
        picam2.close()
        print("Raspberry Pi Camera stopped.")

# -------------------------------------------------------------------------
# 함수: capture_and_save_usb
# 목적: USB 카메라를 사용하여 영상을 캡처하고,
#       일정 시간 간격마다 (interval) 캡처한 영상을 MP4 파일로 저장합니다.
# -------------------------------------------------------------------------
"""
def capture_and_save_usb(shutdown_event, usb_index, output_dir="videos", interval=10):
    # 영상 파일을 저장할 디렉토리가 존재하지 않으면 생성합니다.
    os.makedirs(output_dir, exist_ok=True)
    try:
        # USB 카메라를 열기: 두 번째 인자로 V4L2 백엔드를 명시합니다.
        cap = cv2.VideoCapture(usb_index, cv2.CAP_V4L2)
        if not cap.isOpened():
            print(f"USB Camera (index {usb_index}) could not be opened.")
            return
        print(f"USB Camera (index {usb_index}) started.")

        # 필요에 따라 USB 카메라의 해상도(1920x1080)를 설정합니다.
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # OpenCV VideoWriter용 코덱 설정
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None  # 영상 저장을 위한 VideoWriter 객체 초기화
        start_time = time.time()  # 저장 주기 측정을 위한 시작 시간 기록

        # shutdown_event가 발생할 때까지 반복합니다.
        while not shutdown_event.is_set():
            # USB 카메라로부터 프레임을 읽어옵니다.
            ret, frame = cap.read()
            if not ret:
                print(f"USB Camera (index {usb_index}): Failed to capture frame.")
                break

            # 지정한 간격(interval)마다 새 영상 파일 생성
            if out is None or (time.time() - start_time >= interval):
                if out:
                    # 이전에 사용한 VideoWriter 객체를 닫습니다.
                    out.release()
                    print(f"USB Camera (index {usb_index}): Video saved.")
                # 현재 타임스탬프를 사용하여 파일명 생성
                timestamp = int(time.time())
                filename = os.path.join(output_dir, f"usb_camera_{usb_index}_{timestamp}.mp4")
                # VideoWriter 객체 생성: 파일명, 코덱, FPS(30fps), 해상도 설정
                out = cv2.VideoWriter(filename, fourcc, 30.0, (1920, 1080))
                start_time = time.time()  # 새 저장 주기 시작

            # 읽어온 프레임을 영상 파일에 기록합니다.
            out.write(frame)

    except Exception as e:
        print(f"Error with USB Camera (index {usb_index}): {e}")
    finally:
        # 종료 시 VideoWriter와 카메라 장치를 해제합니다.
        if out:
            out.release()
        if cap:
            cap.release()
        print(f"USB Camera (index {usb_index}) stopped.")
"""

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
    #p_usb = mp.Process(target=capture_and_save_usb, args=(shutdown_event, usb_index, output_dir, interval))
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
