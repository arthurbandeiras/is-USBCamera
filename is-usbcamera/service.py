import json
import os
import logging

from gateway import USBCameraPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():

    config_path = "/app/is-usbcamera/conf/config.json"

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(
            f"Configuration file not found at {config_path}. Please ensure the file exists."
        )
        return
    except json.JSONDecodeError:
        logger.error(
            f"Configuration file at {config_path} is not a valid JSON. Please check the file format."
        )
        return

    logger.info("Starting USBCameraPublisher with the following configuration:")
    for key, value in config.items():
        logger.info(f"{key}: {value}")

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
