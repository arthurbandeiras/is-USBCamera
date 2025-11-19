# 🛠️ Guia de Setup da Câmera Virtual (Raspberry Pi / K8s)

Este documento registra o processo para instalar, compilar e configurar o módulo v4l2loopback em um ambiente Ubuntu Server (Raspberry Pi) e garantir que o dispositivo /dev/video17 esteja disponível no boot para o Kubelet.

## Pré-requisitos

Certifique-se de que seu sistema esteja atualizado e tenha os headers do kernel necessários para a compilação de módulos:

```bash
sudo apt update
sudo apt install -y git build-essential dkms linux-headers-$(uname -r) v4l2loopback-dkms
```

## Passo 1: Criação do Script de Setup (camera_setup.sh)

Este script é responsável por instalar o v4l2loopback (se necessário), carregar o módulo no kernel e, crucialmente, aguardar a estabilização completa do dispositivo V4L2 antes de finalizar.

Crie o arquivo :

```bash
sudo nano /usr/local/bin/camera_setup.sh
```

Preencha o conteúdo do /usr/local/bin/camera_setup.sh com o código abaixo:

```bash
#!/bin/bash
# Script de inicialização para garantir que o v4l2loopback esteja compilado e carregado
# antes do Kubelet iniciar os Pods.

# 1. Instalação de Dependências (Garante que as ferramentas estão prontas)
echo "1/4: Instalando dependências (apt update/install)..."
apt update
apt install -y build-essential dkms git linux-headers-raspi

# 2. Compilação e Instalação do Módulo v4l2loopback
echo "2/4: Clonando e compilando v4l2loopback..."
cd /tmp

# Limpeza e clone
if [ -d "v4l2loopback" ]; then
    rm -rf v4l2loopback
fi

git clone https://github.com/umlaeute/v4l2loopback.git
cd v4l2loopback

echo "3/4: Compilando e instalando o módulo (Isso pode levar tempo)..."
make
make install
cd / && depmod -a

# 3. Carregamento do Módulo (Cria o dispositivo /dev/video17)
echo "4/4: Carregando o módulo v4l2loopback e criando /dev/video17..."
# Certifique-se de que esses parâmetros correspondem ao que o seu Pod Kubernetes espera
modprobe v4l2loopback video_nr=17 card_label="VirtualCam" exclusive_caps=1

# Pausa crucial: Garante que o dispositivo apareça no /dev/ antes que o Kubelet o veja.
DEVICE="/dev/video17"
MAX_TRIES=10
DELAY=2
echo "Aguardando a criação completa do dispositivo $DEVICE..."
 
for i in $(seq 1 $MAX_TRIES); do
    if [ -c "$DEVICE" ]; then
        echo "Dispositivo $DEVICE encontrado e pronto após $i tentativas."
        break
    fi
    echo "Tentativa $i: $DEVICE ainda não está totalmente pronto. Esperando ${DELAY}s..."
    sleep $DELAY
    if [ $i -eq $MAX_TRIES ]; then
        echo "ERRO CRÍTICO: Dispositivo $DEVICE não apareceu após $(($MAX_TRIES * $DELAY)) segundos."
        exit 1
    fi
done

echo "Preparação do ambiente para K8s concluída. Dispositivo $DEVICE está pronto."
```

Defina as permissões de execução:

```bash
sudo chmod +x /usr/local/bin/camera_setup.sh
```

## Passo 2: Criação do Serviço Systemd (v4l2loopback-setup.service)

O serviço systemd deve ser configurado para ser executado no boot e deve usar o usuário root para garantir as permissões necessárias para modprobe e make install.

Crie o arquivo de serviço: 

```bash
sudo nano /etc/systemd/system/v4l2loopback-setup.service
```

Preencha o conteúdo do /etc/systemd/system/v4l2loopback-setup.service com o código abaixo:

```bash
[Unit]
Description=Instala, compila e carrega v4l2loopback para uso do Kubelet
After=network-online.target
Before=kubelet.service containerd.service docker.service
Wants=network-online.target

[Service]
Type=oneshot
# O user/group precisa ter permissão para rodar Docker (adicione o user 'pi' ao grupo 'docker')
# Se você está logado como 'pi', pode usar 'User=pi'
User=root
Group=root
# Define o caminho do script que criamos
TimeoutStartSec=300
ExecStart=/usr/local/bin/camera_setup.sh
# Mantém o status "ativo" mesmo após a conclusão do script
RemainAfterExit=yes


[Install]
# Garante que o serviço será executado no boot
WantedBy=multi-user.target

```

## Passo 3: Ativar e Iniciar o Serviço

Após criar ambos os arquivos, você precisa recarregar o systemd para reconhecer o novo serviço, ativá-lo para que inicie no boot e executá-lo imediatamente:

1. Recarrega a configuração do systemd

    ```bash
    sudo systemctl daemon-reload
    ```

2. Habilita o serviço para iniciar no boot

    ```bash
    sudo systemctl enable v4l2loopback-setup.service
    ```

3. Inicia o serviço imediatamente

    ```bash
    sudo systemctl start v4l2loopback-setup.service
    ```

## Passo 4: Verificação

Verifique o status e os logs para confirmar que o serviço foi executado com sucesso:

1. Verifica o status geral do serviço

    ```bash
    sudo systemctl status v4l2loopback-setup.service
    ```

2. Acompanha os logs em tempo real

    ```
    sudo journalctl -u v4l2loopback-setup.service -f
    ```

    Resultado esperado: **Active: active (exited)**

    O log deve mostrar a linha: Dispositivo /dev/video17 encontrado e pronto após X tentativas.

3. Verifique a existência do dispositivo

    ```bash
    ls -l /dev/video17
    ```