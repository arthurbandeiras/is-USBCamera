from gateway import USBCameraGateway		


def main():
    gateway = USBCameraGateway(
        broker_uri='amqp://guest:guest@localhost:5672',
        camera_idx=0,
    )
    while True:
        gateway.run()


if __name__ == "__main__":
    main()
