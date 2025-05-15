from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder        # ← MJPEG (HW 인코더) 사용
from picamera2.outputs import FileOutput
from datetime import datetime
import os, time, pathlib

# ──────────────────────────────────────────────
PICAM_VIDEO_DIR = pathlib.Path("PICAM_Video")
PICAM_VIDEO_NAME_HEADER = "PICAM"
RECORD_SEC = 5
FPS = 30
FRAME_US = int(1_000_000 / FPS)                   # 33333 µs @30 fps
WIDTH, HEIGHT = 640, 480
# ──────────────────────────────────────────────

def init_cam() -> Picamera2:
    cam = Picamera2()

    cfg = cam.create_video_configuration(
        main={"size": (WIDTH, HEIGHT), "format": "RGB888"},
        controls={"FrameDurationLimits": (FRAME_US, FRAME_US)}  # 고정 fps 설정:contentReference[oaicite:0]{index=0}
    )
    cam.configure(cfg)
    return cam

def record(cam: Picamera2, sec: int):
    PICAM_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = PICAM_VIDEO_DIR / f"{PICAM_VIDEO_NAME_HEADER}_{stamp}.mjpeg"

    enc = MJPEGEncoder()                           # MJPEG → .mjpeg 파일로 저장:contentReference[oaicite:1]{index=1}
    cam.start()
    cam.start_recording(enc, FileOutput(str(fname)))
    time.sleep(sec)
    cam.stop_recording()
    cam.close()                                    # 자원 정리

if __name__ == "__main__":
    cam = init_cam()
    record(cam, RECORD_SEC)
