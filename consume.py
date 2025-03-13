from is_wire.core import Channel, Subscription
from is_msgs.image_pb2 import Image
import cv2
import numpy as np
from google.protobuf.message import DecodeError


def to_np(image):
    buffer = np.frombuffer(image.data, dtype=np.uint8)
    output = cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    return output

def to_image(
    image,
    encode_format: str = ".jpeg",
    compression_level: float = 0.8,
):
    if encode_format == ".jpeg":
        params = [cv2.IMWRITE_JPEG_QUALITY, int(compression_level * (100 - 0) + 0)]
    elif encode_format == ".png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, int(compression_level * (9 - 0) + 0)]
    else:
        return Image()
    cimage = cv2.imencode(ext=encode_format, img=image, params=params)
    return Image(data=cimage[1].tobytes())

channel = Channel("amqp://guest:guest@localhost:5672")

subscription = Subscription(channel)
subscription.subscribe(topic="usb-camera")

while True:

    # Blocks forever waiting for one message from any subscription

    message = channel.consume()
    image = message.unpack(Image)

    img_data = to_np(image)


    cv2.imshow('janela', img_data)

    cv2.waitKey(1)
