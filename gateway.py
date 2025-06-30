import cv2
import time
import threading
import queue

from is_wire.core import Channel, Subscription, ContentType, Message
from is_msgs.image_pb2 import Image


def to_image(
    image,
    encode_format: str = ".jpeg",
    compression_level: float = 0.8,
):
    if encode_format == ".jpeg":
        params = [cv2.IMWRITE_JPEG_QUALITY, int(compression_level * 100)]
    elif encode_format == ".png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, int(compression_level * 9)]
    else:
        return Image()
    cimage = cv2.imencode(ext=encode_format, img=image, params=params)
    return Image(data=cimage[1].tobytes())


class USBCameraGateway:
    def __init__(self, broker_uri, camera_idx):
        self.broker_uri = broker_uri
        self.camera = cv2.VideoCapture(camera_idx)

        # Configurar resolução e MJPEG diretamente
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        self._compression_level = 0.8
        self.channel = Channel(self.broker_uri)
        self.subscription = Subscription(self.channel)

        # Buffer de frames e thread de captura
        self.frame_queue = queue.Queue(maxsize=2)
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

    def _capture_loop(self):
        while True:
            ret, frame = self.camera.read()
            if ret and not self.frame_queue.full():
                self.frame_queue.put(frame)

    def run(self):
        start_time = time.time()

        if self.frame_queue.empty():
            return

        frame = self.frame_queue.get()

        # Compressão JPEG e empacotamento
        img_msg = to_image(frame, ".jpeg", self._compression_level)
        msg = Message(content_type=ContentType.PROTOBUF)
        msg.pack(img_msg)

        # Publicação
        self.channel.publish(msg, topic="CameraGateway.20.Frame")

        elapsed = time.time() - start_time
        fps = 1 / elapsed if elapsed > 0 else 0
        print(f"[INFO] Tempo: {elapsed:.3f}s | FPS real: {fps:.2f}")
