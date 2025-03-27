from is_wire.core import Channel, Subscription, ContentType, Message
from is_msgs.image_pb2 import Image, ColorSpace, ColorSpaces, ImageFormat, ImageFormats, Resolution
import cv2
import time

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
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        self.camera.set(cv2.CAP_PROP_FPS, 20)
        self.camera.set(cv2.CAP_PROP_FOCUS, 255)

        self._compression_level = 0.8
        self.fps = 20
        self.frameTime = 1/self.fps
        self.channel = Channel(self.broker_uri)
        self.subscription = Subscription(self.channel)


    def run(self) -> None:
        # prevTime = time.time()
        # target = self.frameTime + prevTime

        now = time.time()
        # while now < target:
        #     now = time.time()

        # target += self.frameTime

        ret, frame = self.camera.read()
        if not ret:
            print("Erro ao capturar imagem")
            return
    
        self.frame = to_image(frame)
    

        message = Message()
        message.content_type = ContentType.PROTOBUF
        message.pack(self.frame)
    
        self.channel.publish(message, topic='CameraGateway.20.Frame')

        elapsedTime = now - time.time() # prevTime
        # prevTime = now

        realFPS = 1 / elapsedTime

        print(f'T: {elapsedTime} | FPS:  {realFPS}')

        print('publicando')
