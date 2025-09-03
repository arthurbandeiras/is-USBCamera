from gateway import USBCameraPublisher		

def main():
    gateway = USBCameraPublisher(
        broker_uri="amqp://10.20.5.3:30000",
        device="/dev/video17",
        fps=15,
        resolution="1920x1080"
    )
    gateway.run()


if __name__ == "__main__":
    main()

    
