# VM master

## commands 
```shell
sudo dnf update
```

## install docker on almalinux 9
```shell
sudo dnf -y --refresh update
sudo dnf upgrade
sudo dnf -y install yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo systemctl status docker
docker --version  #Docker version 28.5.2,
id
sudo usermod -aG docker alma
```

### Install portainer for managing containers
```shell
docker volume create portainer_data
docker run -d -p 32125:8000 -p 32126:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock \
 -v portainer_data:/data portainer/portainer-ce:2.27.0-alpine
```



## install Kind
```shell
sudo dnf install -y  wget git libffi-devel
wget https://github.com/kubernetes-sigs/kind/releases/download/v0.30.0/kind-linux-amd64
mv kind-linux-amd64 kind
chmod +x kind
sudo mv kind /usr/local/bin/kind
kind version # should be  version 0.30.0
```

## install kubectl
```shell
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/kubectl
# add in .bashrc
alias ks='kubectl'
source <(kubectl completion bash | sed s/kubectl/ks/g)
# check 
kubectl version
# should be version 1.34.1
```

## kind.config
```yaml
---
apiVersion: kind.x-k8s.io/v1alpha4
kind: Cluster
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 32000
    hostPort: 32000
    listenAddress: "0.0.0.0" # Optional, defaults to "0.0.0.0"
    protocol: tcp # Optional, defaults to tcp
- role: worker
```

## Create a cluster
```shell
kind create cluster --name awx --config kind.config
ks version # should be version  v1.34.1+
ks get nodes # see one controle-plane and 1 worker
# kind delete cluster --name awx
```

## install AWX kubernetes operator
```shell
cd
git clone https://github.com/ansible/awx-operator.git
cd awx-operator/
git checkout tags/2.19.1
git log --oneline  # HEAD should be on tag 2.19.1 #hash dd37ebd
kubectl config set-context --current --namespace=awx
```
## kustomization 
```yaml
---
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  # Find the latest tag here: https://github.com/ansible/awx-operator/releases
  - github.com/ansible/awx-operator/config/default?ref=2.19.1
# Set the image tags to match the git version from above
images:
  - name: quay.io/ansible/awx-operator
    newTag: 2.19.1

# Specify a custom namespace in which to install AWX
namespace: awx
```
## install awx operator
```shell
kubectl apply -k .
```
## awx-demo.yml 
```yaml
---
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx-demo
spec:
  service_type: nodeport
  nodeport_port: 32000
```
## install awx 
```shell
kubectl create -f awx-demo.yml
```
wait 10 minutes

## User AWX
username admin
Password uses the command below
```shell
kubectl get secret -n awx  awx-demo-admin-password -o jsonpath="{.data.password}" | base64 --decode ; echo
```
Change your password to a simple one
## Web access
```
kubectl port-forward -n awx service/awx-demo-service 30540:80 --address='0.0.0.0' &
```
access to AWX with http://<ip>:30540


## Troubleshooting to prevent job template failure in AWX
```shell
echo fs.inotify.max_user_watches=655360 | sudo tee -a /etc/sysctl.conf
echo fs.inotify.max_user_instances=1280 | sudo tee -a /etc/sysctl.conf
echo fs.file-max = 2097152 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```
