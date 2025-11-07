🛠️ Guia de Setup da Câmera Virtual (Raspberry Pi / K8s)

Este documento registra o processo para instalar, compilar e configurar o módulo v4l2loopback em um ambiente Ubuntu Server (Raspberry Pi) e garantir que o dispositivo /dev/video17 esteja disponível no boot para o Kubelet.

Pré-requisitos

Certifique-se de que seu sistema esteja atualizado e tenha os headers do kernel necessários para a compilação de módulos:

sudo apt update
sudo apt install -y git build-essential dkms linux-headers-$(uname -r) v4l2loopback-dkms


Passo 1: Criação do Script de Setup (camera_setup.sh)

Este script é responsável por instalar o v4l2loopback (se necessário), carregar o módulo no kernel e, crucialmente, aguardar a estabilização completa do dispositivo V4L2 antes de finalizar.

Crie o arquivo e defina as permissões de execução:

sudo touch /usr/local/bin/camera_setup.sh   ***USEI O NANO***
sudo chmod +x /usr/local/bin/camera_setup.sh


Preencha o conteúdo do /usr/local/bin/camera_setup.sh com o código abaixo:   ***PEGA O QUE TA NA RASP2***

#!/bin/bash

V4L2_LOOPBACK_REPO="/tmp/v4l2loopback"
DEVICE="/dev/video17"

echo "1/4: Instalando dependências e verificando headers..."

# A compilação é um fallback caso o dkms não tenha funcionado
if [ ! -d "$V4L2_LOOPBACK_REPO" ]; then
    echo "2/4: Clonando e compilando v4l2loopback..."
    cd /tmp
    git clone [https://github.com/umlaeute/v4l2loopback.git](https://github.com/umlaeute/v4l2loopback.git) "$V4L2_LOOPBACK_REPO"
    cd "$V4L2_LOOPBACK_REPO"
    
    # Compilação e instalação (não precisa de sudo, pois o script roda como root)
    make
    make install
    
    # Gerar os arquivos de cache do kernel de forma robusta
    ( cd / && depmod -a )
    
    cd /
    rm -rf "$V4L2_LOOPBACK_REPO"
else
    echo "2/4: Diretório de compilação já existe, pulando clone/compilação."
fi

echo "3/4: Descarregando e recarregando o módulo para garantir limpeza..."
modprobe -r v4l2loopback 2>/dev/null || true # Ignora erro se o módulo não estiver carregado

# 4/4: Carregando o módulo v4l2loopback e criando /dev/video17...
# exclusive_caps=1 é crucial para o PyAV/FFmpeg funcionar
modprobe v4l2loopback video_nr=17 card_label="VirtualCam" exclusive_caps=1

# --- Bloco de Espera Corrigido (Mitigando a Race Condition) ---
MAX_TRIES=10
DELAY=1 
echo "Aguardando a criação completa e estabilização do dispositivo $DEVICE..."

for i in $(seq 1 $MAX_TRIES); do
    # Verifica se o arquivo do dispositivo existe e é um arquivo de bloco (c)
    if [ -c "$DEVICE" ]; then
        echo "Dispositivo $DEVICE encontrado e pronto após $i tentativas."
        
        # Correção final: Espera adicional para o kernel finalizar a inicialização do V4L2
        echo "Aguardando 2 segundos adicionais para a inicialização do V4L2..."
        sleep 2 
        
        break
    fi
    echo "Tentativa $i: $DEVICE ainda não está totalmente pronto. Esperando ${DELAY}s..."
    sleep $DELAY
    if [ $i -eq $MAX_TRIES ]; then
        echo "ERRO CRÍTICO: Dispositivo $DEVICE não apareceu após $(($MAX_TRIES * $DELAY)) segundos."
        exit 1
    fi
done
# -----------------------------------------------------------------

echo "Preparação do ambiente para K8s concluída. Dispositivo $DEVICE está pronto."


Passo 2: Criação do Serviço Systemd (v4l2loopback-setup.service)

O serviço systemd deve ser configurado para ser executado no boot e deve usar o usuário root para garantir as permissões necessárias para modprobe e make install.

Crie o arquivo de serviço: ***PEGA O QUE TA NA RASP2***

sudo touch /etc/systemd/system/v4l2loopback-setup.service ***USEI O NANO***


Preencha o conteúdo do /etc/systemd/system/v4l2loopback-setup.service com o código abaixo:

[Unit]
Description=Instala, compila e carrega v4l2loopback para uso do Kubelet
After=network.target

[Service]
# CRUCIAL: Deve ser executado como root para manipulação de módulos do kernel
User=root
Type=oneshot
ExecStart=/usr/local/bin/camera_setup.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target


Passo 3: Ativar e Iniciar o Serviço

Após criar ambos os arquivos, você precisa recarregar o systemd para reconhecer o novo serviço, ativá-lo para que inicie no boot e executá-lo imediatamente:

# Recarrega a configuração do systemd
sudo systemctl daemon-reload

# Habilita o serviço para iniciar no boot
sudo systemctl enable v4l2loopback-setup.service

# Inicia o serviço imediatamente
sudo systemctl start v4l2loopback-setup.service


Passo 4: Verificação

Verifique o status e os logs para confirmar que o serviço foi executado com sucesso:

# Verifica o status geral do serviço
sudo systemctl status v4l2loopback-setup.service

# Acompanha os logs em tempo real
sudo journalctl -u v4l2loopback-setup.service -f


Resultado esperado:

Active: active (exited)

O log deve mostrar a linha: Dispositivo /dev/video17 encontrado e pronto após X tentativas.

Verifique a existência do dispositivo: ls -l /dev/video17