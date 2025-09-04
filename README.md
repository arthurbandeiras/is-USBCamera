# is-USBCamera

Para settar a câmera "virtual" no host:
```
sudo modprobe v4l2loopback video_nr=17 card_label="VirtualCam" exclusive_caps=1
```

Para rodar o projeto:
```
docker run --rm -it   --device=/dev/video0:/dev/video0   --device=/dev/video1:/dev/video1   --device=/dev/video17:/dev/video17 -v ./config.json:/app/options.json  antoniosto/is-usbcamera
```
