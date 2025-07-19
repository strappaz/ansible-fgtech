# Install Sandbox on Almalinux 

VM GCP 4 cores 12 GB ram, 50 GB disk

# Pre-requiste 
```shell
sudo dnf update -y
sudo dnf install git wget -y
git clone https://github.com/crunchy-devops/ansible-fgtech.git
wget https://www.python.org/ftp/python/3.13.5/Python-3.13.5.tgz
tar -zxvf Python-3.13.5.tgz
sudo dnf install openssl-devel bzip2-devel libffi-devel -y
sudo dnf groupinstall "Development Tools" -y
cd Python-3.13.5
make -j4
make test
sudo make install
# latest version of ansible

```


kubectl port-forward -n awx service/awx-demo-service 30004:80 --address='0.0.0.0'


## Troubleshooting
```shell
echo fs.inotify.max_user_watches=655360 | sudo tee -a /etc/sysctl.conf
echo fs.inotify.max_user_instances=1280 | sudo tee -a /etc/sysctl.conf
echo fs.file-max = 2097152 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```