import json
import os

from gateway import USBCameraPublisher


def main():

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "..", "conf", "config.json")

    with open(config_path, "r") as f:
        config = json.load(f)

    gateway = USBCameraPublisher(
        broker_uri=config["broker_uri"],
        device=config["device"],
        fps=config["framerate"],
        resolution=config["resolution"],
        id=config["camera_id"],
    )
    gateway.run()


if __name__ == "__main__":
    main()
