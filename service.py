from gateway import USBCameraGateway		

def main():
    gateway = USBCameraGateway(
        broker_uri='amqp://10.20.5.3:30000',
        camera_idx=0,
    )
    while True:
        gateway.run()

if __name__ == "__main__":
    main()
