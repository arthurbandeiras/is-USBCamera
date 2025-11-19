# 🐳 Instalação do Docker Engine no Ubuntu Server 22.04 (Raspberry Pi/Arm64)

Este guia documenta o processo de instalação da versão mais recente do **Docker Engine, Docker CLI, containerd e Docker Compose** no Ubuntu Server 22.04, utilizando o repositório oficial do Docker.

> 📝 **Nota:** Estes comandos são projetados para sistemas baseados em Debian/Ubuntu, incluindo seu **Raspberry Pi 4 rodando Ubuntu Server 22.04 (Arquitetura Arm64)**.

---

## Pré-requisitos

* Acesso ao terminal com privilégios `sudo`.
* Conexão com a internet.

---

## 🚀 Etapas de Instalação

Siga as etapas abaixo sequencialmente.

### 1. Atualizar Pacotes e Instalar Dependências

Primeiro, atualize a lista de pacotes e instale os utilitários necessários para adicionar o repositório HTTPS.

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
```

---

### 2. Adicionar a Chave GPG Oficial do Docker

Para garantir a segurança dos pacotes, adicione a chave GPG oficial do Docker ao seu sistema.

```bash
# Cria o diretório para as chaves GPG
sudo install -m 0755 -d /etc/apt/keyrings

# Baixa e desarma a chave GPG do Docker
curl -fsSL [https://download.docker.com/linux/ubuntu/gpg](https://download.docker.com/linux/ubuntu/gpg) | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Garante que as permissões de leitura do arquivo GPG estão corretas
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

---

### 3. Configurar o Repositório Estável do Docker

Adicione o repositório oficial do Docker à lista de fontes do APT, garantindo que a arquitetura (`dpkg --print-architecture`) e a versão do Ubuntu (`$VERSION_CODENAME`) sejam detectadas corretamente.

```bash
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

---

### 4. Instalar os Componentes do Docker

Atualize o índice de pacotes novamente (agora incluindo o repositório Docker) e instale todos os componentes principais: **Docker Engine**, **CLI**, **containerd** e **plugins**.

```bash
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---

### 5. Verificar a Instalação

Execute o contêiner de teste `hello-world` para confirmar que o Docker Engine está funcionando corretamente.

```bash
sudo docker run hello-world
```

---

### 6. Configurar o Acesso sem `sudo` (Opcional, mas Recomendado)

Para executar comandos do Docker sem precisar do prefixo `sudo`, adicione seu usuário ao grupo `docker`.

>⚠️ IMPORTANTE: Você precisa sair e entrar novamente na sua 
>sessão SSH/terminal para que esta alteração de grupo entre em 
>vigor.
>>

```bash
sudo usermod -aG docker ${USER}
```

Após sair e entrar novamente, você pode testar o Docker sem `sudo`.

---