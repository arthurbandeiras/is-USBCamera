#!/bin/bash

# === 1. Configura a câmera real ===
v4l2-ctl -d /dev/video0 --set-ctrl=auto_exposure=1                       # Modo Manual
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_dynamic_framerate=0         # Desativa ajuste automático de FPS
v4l2-ctl -d /dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat=MJPG
v4l2-ctl -d /dev/video0 --set-parm=30                                   # Define FPS para 30

# === 2. Reinicia o módulo v4l2loopback com parâmetros fixos ===
sudo modprobe -r v4l2loopback
sudo modprobe v4l2loopback video_nr=17 card_label="LoopbackCam" exclusive_caps=1 max_buffers=3 latency=0

# === 3. Inicia o FFmpeg em background, redirecionando o vídeo ===
ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1920x1080 \
       -i /dev/video0 -c:v copy -f v4l2 /dev/video17 &

FFMPEG_PID=$!

# === 4. Aguarda o FFmpeg abrir a câmera, e então reaplica a exposição ===
sleep 1
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_time_absolute=300

# === 5. Aguarda o FFmpeg encerrar (opcional) ===
wait $FFMPEG_PID
