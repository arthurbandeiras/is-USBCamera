#!/bin/bash

# --- 1. Configura a câmera real ---
# Configurações iniciais da câmera real (/dev/video0)
v4l2-ctl -d /dev/video0 --set-ctrl=auto_exposure=1
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_dynamic_framerate=0
v4l2-ctl -d /dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat=MJPG
v4l2-ctl -d /dev/video0 --set-parm=30

# --- 2. Inicia o FFmpeg em background, redirecionando o vídeo ---
# O FFmpeg lê a câmera USB e a reescreve no dispositivo virtual /dev/video17
ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1920x1080 \
       -i /dev/video0 -c:v copy -f v4l2 /dev/video17 &

FFMPEG_PID=$!

# --- 3. Aguarda a estabilização e aplica o controle de exposição ---
# É crucial esperar que o FFmpeg abra a porta de entrada (video0) e crie a de saída (video17).
# Uma pausa fixa de 3 segundos é mais segura do que 1 segundo, dada a natureza do problema.
echo "Aguardando 3 segundos para estabilização do pipeline FFmpeg..."
sleep 3 

# Reaplicar a exposição DEPOIS que o FFmpeg a abriu.
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_time_absolute=300

# --- 4. Inicia o serviço Python e aguarda ---
# O processo Python agora está no foreground, e o Shell aguarda que ele termine.
# O FFmpeg continua rodando em background (PID=$FFMPEG_PID) e alimenta o video17.
echo "Iniciando serviço Python (USBCameraPublisher)..."
python3 is-usbcamera/service.py

# --- 5. Limpeza (Só será alcançado se o serviço Python for interrompido) ---
# Se o serviço Python for interrompido (ex: SIGINT), o shell continuará aqui.
echo "Serviço Python encerrado. Finalizando FFmpeg (PID $FFMPEG_PID)..."
kill $FFMPEG_PID
wait $FFMPEG_PID 2>/dev/null # Aguarda a morte do processo FFmpeg
echo "Startup script concluído."