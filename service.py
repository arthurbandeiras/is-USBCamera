from gateway import USBCameraPublisher		
import json

def main():
    
    options = json.load(open('./options.json', 'r'))

    gateway = USBCameraPublisher(
        broker_uri=options["broker_uri"],
        device=options["device"],
        fps=options["framerate"],
        resolution=options["resolution"],
        id=options["camera_id"]
    )
    gateway.run()


if __name__ == "__main__":
    main()

    
