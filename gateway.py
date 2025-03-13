from is_wire.core import Channel, Subscription, ContentType, Message
import cv2
import image_pb2 #arquivo gerado pelo protoc


class USBCameraGateway(object):
      
    def __init__(self, broker_uri, camera_idx):
            
        self.broker_uri = broker_uri
        self.camera = cv2.VideoCapture(camera_idx)


    def run(self) -> None:
        
        channel = Channel(self.broker_uri)
        subscription = Subscription(channel)

        ret, frame = self.camera.read()
        if not ret:
            print("Erro ao capturar imagem")
            return
    
        ok, encoded_image = cv2.imencode('.jpg', frame)
        if not ok:
            print("Erro ao codificar imagem")
            return
        
        #acho que tem que trocar isso aqui
        #Procure por "driver"
        '''
        message = Message()
        message.pack(self.driver.to_image(image))
        '''
        image_msg = image_pb2.ImageMessaege()
        image_msg.image_data = encoded_image.tobytes()
        image_msg.format = 'jpeg'

        message = Message()
        message.content_type = ContentType.PROTOBUF
        message.content = image_msg.SerializeToString()

        channel.publish(message)

    






"""def run(self) -> None:
        service_name = "CameraGateway"
        time.sleep(2) #tirar(?)
        publish_channel = Channel(self.broker_uri)
        rpc_channel = Channel(self.broker_uri)

        server = ServiceProvider(channel=rpc_channel)
        #logging = LogInterceptor()
        #tracing = TracingInterceptor(exporter=exporter)
        #server.add_interceptor(interceptor=logging)
        #server.add_interceptor(interceptor=tracing)

        self.driver.start_capture() #start na thread
        
        while True:
            image = self.driver.grab_image() #trocar para o cv2.seilaoq
			'''se quiser, pode até manter a situação de tracing da publicação,
			mas, tem que aprender a usar'''
            message = Message()
            message.pack(self.driver.to_image(image))
            message.topic = "{}.{}.Frame".format(service_name, self.id)

            if len(image.data) > 0:
                publish_channel.publish(message=message)
                self.logger.info("Published image") 
            else:
                self.logger.warn("No image captured.")
            try:
                message = rpc_channel.consume(timeout=0)
                if server.should_serve(message):
                    server.serve(message)
            except socket.timeout:
                pass


def start_capture(self):
	self.-stopped = False
    selfself._thread = Thread(target=self._update, daemon=True)
	self._thread.start()"""
