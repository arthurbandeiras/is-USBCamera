# Guia de utilização do repositório em arquitetura amd64

Este guia apresenta o passo a passo de utilização do projeto não containerizado para a arquitetura amd64.

> **🚨 AVISO IMPORTANTE 🚨**
>
> O repositório foi originalmente desenvolvido para a criação de novas câmeras para o Espaço Inteligente, com a utilização de raspberry's e webcams. Entretanto, para teste local, foi desenvolvido esse guia.
>> 


## Etapa 1: Configuração da câmera real

```bash
v4l2-ctl -d /dev/video0 --set-ctrl=auto_exposure=1
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_dynamic_framerate=0         
v4l2-ctl -d /dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat=MJPG
v4l2-ctl -d /dev/video0 --set-parm=30                                   
```

## Etapa 2: Reinicia o módulo v4l2loopback com parâmetros fixos

```bash
sudo modprobe -r v4l2loopback
sudo modprobe v4l2loopback video_nr=17 card_label="LoopbackCam" exclusive_caps=1 max_buffers=3 latency=0                             
```

## Etapa 3: Inicia o FFmpeg (captura da câmera real)

```bash
ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1920x1080 -i /dev/video0 -c:v copy -f v4l2 /dev/video17
```

## Etapa 4: Confirma o set da exposição

Em outro terminal:

```bash
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_time_absolute=300
```

## Etapa 5: Rodar o projeto

Mude a variável `config_path` no arquivo is-usbcamera/service.py para:

```bash
config_path="./conf/config.json"
```

```bash
cd ./is-usbcamera
python3 service.py
```

## Extras:
Alguns comandos que podem vir a ser úteis.

1. **Para listar os dispositivos:**
    Se aparecer /dev/video17 depois da Etapa 2, ótimo :)
    ```
    v4l2-ctl --list-devices
    ```

2. **Para capturar a 1280x720:**
    Substituir o comando da Etapa 3 por:
    ```
    ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1280x720 -i /dev/video0 -c:v copy -f v4l2 /dev/video17
    ```

