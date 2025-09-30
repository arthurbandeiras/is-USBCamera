# is-USBCamera

##Raspberry Pi OS

```
sudo apt update
sudo apt install -y build-essential raspberrypi-kernel-headers dkms git
git clone https://github.com/umlaeute/v4l2loopback.git
cd v4l2loopback
sudo make && sudo make install
sudo depmod -a
sudo modprobe v4l2loopback video_nr=17 card_label="VirtualCam" exclusive_caps=1
```

##Ubuntu Server 22.04
```
sudo apt update
sudo apt install -y build-essential dkms git linux-headers-raspi
git clone https://github.com/umlaeute/v4l2loopback.git
cd v4l2loopback
sudo make
sudo make install
sudo depmod -a
cd ..
sudo modprobe v4l2loopback video_nr=17 card_label="VirtualCam" exclusive_caps=1
```

Para rodar o projeto:
```
docker run --rm -it   --device=/dev/video0:/dev/video0   --device=/dev/video1:/dev/video1   --device=/dev/video17:/dev/video17 -v ./config.json:/app/options.json  antoniosto/is-usbcamera
```


## Para configurar o kubernetes (entrar no cluster):

```
mkdir -p ~/.kube
scp labvisio@10.20.5.1:.kube/config ~/.kube/config
chmod 600 ~/.kube/config
```
