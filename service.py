from gateway import USBCameraGateway
import time

def main():
    gateway = USBCameraGateway(
        broker_uri='amqp://10.20.5.3:30000',
        device='/dev/video1',
        resolution=(1280, 720),
        fps=20
    )
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
