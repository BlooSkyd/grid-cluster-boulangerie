Install minikub sur une VM Ubuntu22.04


sudo apt update && sudo apt upgrade 
# I installation Docker
spurce : https://docs.docker.com/engine/install/ubuntu/
## Add Docker's official GPG key:
```sh
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

## Add the repository to Apt sources:
```sh 
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```
## Verifier le fonctionnement
```sh 
sudo docker run hello-world
```
# II Installation minikub
pré requis:
- CPU: 2
- RAM: 8 Go
## a. minikub
source : https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Fbinary+download
```sh
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
sudo usermod -aG docker $USER && newgrp docker
minikube start
```

## b.kubctl
source : https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
```sh
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
kubectl cluster-info
```

## c. Dépanner 
Si minikube ne démarre pas correctement je sais pas pourquoi kubelet et l'api server refuse de démarrer.

Alors faire:
```sh
minikube delete
minikube start
```