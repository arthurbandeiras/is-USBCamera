FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    v4l-utils \
    build-essential \
    libturbojpeg0 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia todo o projeto (inclui startup_camera.sh e service.py)
COPY . .

# Garante que o script de inicialização é executável
RUN chmod +x startup_camera.sh

# Ao iniciar o container: roda o startup.sh e depois o serviço
CMD ["bash", "-c", "./startup_camera.sh & python3 service.py"]
