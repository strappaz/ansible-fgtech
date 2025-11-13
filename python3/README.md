# Python3 install 

## on Centos7
```shell
yum install centos-release-scl
sed -i 's/mirror.centos.org/vault.centos.org/g' /etc/yum.repos.d/*.repo   \
    && sed -i 's/^#.*baseurl=http/baseurl=http/g' /etc/yum.repos.d/*.repo \
    && sed -i 's/^mirrorlist=http/#mirrorlist=http/g' /etc/yum.repos.d/*.repo
yum install  rh-python38
ln -s /opt/rh/rh-python38/root/usr/bin/python3 /usr/bin/python3
python3 -V


## from sources
```shell
sudo dnf groupinstall -y "Development tools"
cd /tmp/
wget https://www.python.org/ftp/python/3.13.9/Python-3.13.9.tgz
tar xzf Python-3.13.9.tgz
cd Python-3.13.9

./configure --prefix=/opt/python3139/ --enable-optimizations --with-lto --with-computed-gotos --with-system-ffi 
make -j "$(nproc)"
sudo make altinstall

```