FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    v4l-utils \
    build-essential \
    libturbojpeg0 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# O Dockerfile deve ser executado do diretório raiz do projeto (is-usbcamera)
COPY is-usbcamera/conf /app/is-usbcamera/conf
COPY is-usbcamera/gateway.py /app/is-usbcamera/gateway.py
COPY is-usbcamera/service.py /app/is-usbcamera/service.py
COPY is-usbcamera/startup_camera.sh .

RUN chmod +x startup_camera.sh

CMD ["./startup_camera.sh"]
