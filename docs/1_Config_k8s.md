# Instalação do Kubernetes v1.25 no Raspberry Pi com Ubuntu Server 22.04

Este guia apresenta o passo a passo completo para instalar as ferramentas do Kubernetes (`kubeadm`, `kubelet` e `kubectl`) na versão específica **1.25** em um Raspberry Pi 4 (ou superior) rodando Ubuntu Server 22.04.

> **🚨 AVISO DE SEGURANÇA IMPORTANTE 🚨**
>
> Este guia utiliza um método que **desativa a verificação de segurança** do repositório de pacotes do Kubernetes (`[trusted=yes]`). Isso é necessário porque a chave de assinatura para a versão **1.25** (que é uma versão antiga e sem suporte oficial) já expirou.
>> 
## Pré-requisitos

-   Raspberry Pi 4 ou superior.
-   Ubuntu Server (versão 22.04 LTS ou compatível) instalado.
-   Acesso ao terminal com privilégios `sudo`.
-   Conexão com a internet.

## Etapa 1: Preparação do Sistema

Estes comandos preparam o sistema operacional para atender aos pré-requisitos do Kubernetes.

1.  **Desabilitar a memória swap:**
    ```bash
    sudo swapoff -a
    sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
    ```

2.  **Carregar módulos de kernel necessários:**
    ```bash
    cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
    overlay
    br_netfilter
    EOF

    sudo modprobe overlay
    sudo modprobe br_netfilter
    ```

3.  **Configurar parâmetros do `sysctl` para a rede do Kubernetes:**
    ```bash
    cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
    net.bridge.bridge-nf-call-iptables  = 1
    net.bridge.bridge-nf-call-ip6tables = 1
    net.ipv4.ip_forward                 = 1
    EOF

    sudo sysctl --system
    ```

## Etapa 2: Instalação do Container Runtime (containerd)

O Kubernetes precisa de um container runtime para executar os contêineres. Usaremos o `containerd`.

1.  **Instalar o `containerd`:**

    ```bash
    sudo apt-get update
    sudo apt-get install -y containerd
    ```

2.  **Configurar o `containerd`:**

    Crie o arquivo de configuração padrão e ajuste-o para usar o `systemd` como cgroup driver, que é o recomendado pelo `kubelet`.
    ```bash
    sudo mkdir -p /etc/containerd
    sudo containerd config default | sudo tee /etc/containerd/config.toml
    sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
    ```

    Cgroups, particularmente os *memory cgroups*, muitas vezes, não estão totalmente habilitados por padrão nos kernels do Raspberry Pi. Para habilitá-los, você precisa modificar os parâmetros de inicialização do kernel. 

    ```bash
    sudo nano /boot/firmware/cmdline.txt
    ```

    Adicione os seguintes parâmetros ao fim da linha existente no arquivo:

    ```bash
    cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1
    ```

3.  **Reiniciar e habilitar o serviço do `containerd`:**

    ```bash
    sudo systemctl restart containerd
    sudo systemctl enable containerd
    ```

4.  **Reboot da Raspberry**

    Necessário para que as alterações nos parâmetros de inicialização do kernel sejam implementadas
    ```bash
    sudo reboot
    ```

## Etapa 3: Instalação do `kubeadm`, `kubelet` e `kubectl` (v1.25)

Agora, instalaremos as ferramentas do Kubernetes a partir do repositório oficial, utilizando a flag que desativa a verificação de segurança.

1.  **Instalar pacotes de pré-requisito para o `apt`:**

    ```bash
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl
    ```

2.  **Adicionar o repositório do Kubernetes v1.25 (com a flag `trusted=yes`):**

    ```bash
    echo "deb [trusted=yes] https://pkgs.k8s.io/core:/stable:/v1.25/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    ```

3.  **Instalar as ferramentas do Kubernetes:**

    ```bash
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    ```

4.  **Marcar os pacotes para não serem atualizados automaticamente:**

    Isso previne que uma atualização acidental do sistema (`apt upgrade`) mude a versão do Kubernetes.
    ```bash
    sudo apt-mark hold kubelet kubeadm kubectl
    ```

## Etapa 4: Verificação

1. Verifique se todos os componentes foram instalados corretamente checando suas versões.

    ```bash
    kubelet --version
    # Deverá retornar algo como: Kubernetes v1.25.x

    kubeadm version
    # Deverá retornar a versão do kubeadm
    ```

    Após instalar o `kubeadm`, você precisa inicializar o Control Plane (se este for o nó mestre) 
    ou juntar o nó ao cluster existente (se for um nó de trabalho). Isso será feito na etapa 5 (note que
    somente uma etapa 5 será realizada, uma vez que ou já existe um cluster com um Control Plane definido, ou
    criaremos um novo cluster do zero)


## Etapa 5a: Entrar no cluster k8s existente

1. No control plane, devemos pegar o token de junção e imprimir o comando completo que a nossa rasp precisa executar.

    ```bash
    sudo kubeadm token create --print-join-command
    ```

2. Copie o comando recebido, adicione `sudo` antes do comando e execute na Raspberry que estamos configurando.

3. Agora, para finalizar, precisamos do arquivo de configuração. Para isso, execute na rasp a ser configurada:

    ```bash 
    mkdir -p .kube/
    scp labvisio@10.20.5.21:/home/labvisio/.kube/config .kube/config
    ```
    Para testar:

    ```bash
    kubectl get nodes -o wide
    ```

    Aqui, o retorno deve ser uma lista com detalhes de todos os nós exitentes no cluster. \
    Pronto! Acabam aqui as configurações necessárias no k8s.


## Etapa 5b: Inicialização do Cluster e Instalação do Calico

Se esta for a primeira máquina do seu cluster, execute o comando `kubeadm init`. A flag `--pod-network-cidr` é crucial para o Calico:

1. **Inicializar o Control Plane**

    ```bash
    # Ajuste o endereço IP se necessário. O CIDR do Pod (192.168.0.0/16) é o padrão do Calico
    sudo kubeadm init --pod-network-cidr=192.168.0.0/16
    ```

⚠️ Guarde a linha de comando kubeadm join que será exibida ao final! Ela é necessária para adicionar nós de trabalho.

2. **Configurar o Acesso ao Cluster:**

    ```bash
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    ```

3. **Instalar o Calico CNI**

    ```bash
    kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.30.3/manifests/calico.yaml
    ```    

        
    > ⚠️ Nota: Devido ao grande tamanho do pacote de Definições de Recursos Customizados (CRD bundle), o comando `kubectl apply` 
    > pode exceder os limites de requisição (request limits) do servidor de API do Kubernetes.
    > Em vez disso, utilize `kubectl create` ou `kubectl replace`.
    >>


    Verificar a instalação:

    ```bash
    kubectl get nodes
    watch kubectl get pods -n kube-system
    ```

    Aguarde até que os pods do Calico e do Control Plane estejam em estado `Running` e que o seu nó mestre esteja em estado `Ready`.