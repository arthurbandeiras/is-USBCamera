# is-USBCamera
```
docker run --rm -it   --device=/dev/video0:/dev/video0   --device=/dev/video1:/dev/video1   --device=/dev/video17:/dev/video17 -v ./config.json:/app/options.json  antoniosto/is-usbcamera
```
