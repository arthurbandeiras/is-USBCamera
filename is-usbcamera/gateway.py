import queue
import threading
import time

import av
from is_msgs.image_pb2 import Image
from is_wire.core import Channel, ContentType, Message


class USBCameraPublisher:
    def __init__(self, broker_uri, device="/dev/video17", fps=15, resolution="1920x1080", id="20"):
        self.broker_uri = broker_uri
        self.device = device
        self.target_fps = fps
        self.frame_queue = queue.Queue(maxsize=1)
        self.running = True
        self.id = id

        self.container = av.open(
            self.device,
            format="v4l2",
            options={"input_format": "mjpeg", "video_size": resolution, "framerate": str(fps)},
        )

        self.stream = self.container.streams.video[0]
        self.channel = Channel(self.broker_uri)

    def capture_loop(self):
        interval = 1.0 / self.target_fps
        next_frame_time = time.perf_counter()

        for packet in self.container.demux(self.stream):
            if not self.running:
                break
            if packet.dts is None:
                continue

            now = time.perf_counter()
            if now >= next_frame_time:
                try:
                    jpeg_bytes = bytes(packet)

                    if self.frame_queue.full():
                        self.frame_queue.get_nowait()
                    self.frame_queue.put_nowait(jpeg_bytes)

                    next_frame_time += interval
                    if now > next_frame_time + interval:
                        next_frame_time = now + interval
                except Exception as e:
                    print("Erro na captura:", e)

        print("⚠️ Loop de captura finalizado.")

    def publish_loop(self):
        while self.running:
            try:
                jpeg_bytes = self.frame_queue.get(timeout=1)
                img_msg = Image(data=jpeg_bytes)
                msg = Message(content_type=ContentType.PROTOBUF)
                msg.pack(img_msg)
                self.channel.publish(msg, topic=f"CameraGateway.{self.id}.Frame")
            except queue.Empty:
                continue

    def run(self):
        t1 = threading.Thread(target=self.capture_loop, daemon=True)
        t2 = threading.Thread(target=self.publish_loop, daemon=True)
        t1.start()
        t2.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Encerrando...")
            self.running = False
            t1.join()
            t2.join()
            self.container.close()
            print("Finalizado.")
