from is_wire.core import Channel, Subscription, ContentType, Message
from is_msgs.image_pb2 import Image, ColorSpace, ColorSpaces, ImageFormat, ImageFormats, Resolution
import cv2

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

class USBCameraGateway(object):
      
    def __init__(self, broker_uri, camera_idx):
            
        self.broker_uri = broker_uri
        self.camera = cv2.VideoCapture(camera_idx)
        self._compression_level = 0.8


    def run(self) -> None:
        
        channel = Channel(self.broker_uri)
        subscription = Subscription(channel)

        ret, frame = self.camera.read()
        if not ret:
            print("Erro ao capturar imagem")
            return
    
        self.frame = to_image(frame)

        message = Message()
        message.content_type = ContentType.PROTOBUF
        message.pack(self.frame)
    
        channel.publish(message, topic='usb-camera')

        print('publicando')