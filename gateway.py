import av
import time
import threading
import queue
import numpy as np
import cv2

from is_wire.core import Channel, Subscription, Message, ContentType
from is_msgs.image_pb2 import Image

def to_image(image, encode_format: str = ".jpeg", compression_level: float = 0.8):
    if encode_format == ".jpeg":
        params = [cv2.IMWRITE_JPEG_QUALITY, int(compression_level * 100)]
    elif encode_format == ".png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, int(compression_level * 9)]
    else:
        return Image()
    result, buffer = cv2.imencode(encode_format, image, params)
    if result:
        return Image(data=buffer.tobytes())
    else:
        return Image()

class USBCameraGateway:
    def __init__(self, broker_uri, device="/dev/video1", resolution=(1920, 1080), fps=20):
        self.broker_uri = broker_uri
        self.device = device
        self.resolution = resolution
        self.target_fps = fps
        self.frame_interval = 1.0 / self.target_fps

        self.channel = Channel(self.broker_uri)
        self.subscription = Subscription(self.channel)

        self.frame_queue = queue.Queue(maxsize=3)

        # Threads
        threading.Thread(target=self._capture_loop, daemon=True).start()
        threading.Thread(target=self._publisher_loop, daemon=True).start()

    def _capture_loop(self):
        print("[INFO] Iniciando captura com PyAV...")
        container = av.open(
            self.device,
            format="v4l2",
            options={
                "framerate": str(self.target_fps),
                "video_size": f"{self.resolution[0]}x{self.resolution[1]}",
                "pixel_format": "mjpeg"
            },
        )

        for frame in container.decode(video=0):
            # Converter para ndarray (formato OpenCV: H x W x 3)
            img = frame.to_ndarray(format="bgr24")
            try:
                self.frame_queue.put(img, timeout=0.01)
            except queue.Full:
                pass

    def _publisher_loop(self):
        count = 0
        start_time = time.time()

        while True:
            try:
                frame = self.frame_queue.get(timeout=0.01)

                # Codificar e empacotar
                img_msg = to_image(frame, ".jpeg", 0.9)
                msg = Message(content_type=ContentType.PROTOBUF)
                msg.pack(img_msg)

                self.channel.publish(msg, topic="CameraGateway.20.Frame")
                count += 1

                # Limitar FPS
                #time.sleep(self.frame_interval)

                # Log de FPS
                if time.time() - start_time >= 1.0:
                    print(f"[BROKER] {count} fps publicado")
                    print(frame.shape)
                    count = 0
                    start_time = time.time()

            except queue.Empty:
                continue
