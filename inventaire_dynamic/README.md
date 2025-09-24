# inventaire dynamique 


## Install Zabbix 
```shell
# install db
docker run -d --name db -e POSTGRES_PASSWORD=password  -v data:/bitnami/postgresql \
  -p 30452:5432 bitnamilegacy/postgresql:17.6.0-debian-12-r4
```  
## install Zabbix packages
```shell
sudo rpm -Uvh https://repo.zabbix.com/zabbix/7.4/release/alma/9/noarch/zabbix-release-latest-7.4.el9.noarch.rpm
sudo dnf clean all 
sudo dnf  -y install zabbix-server-pgsql zabbix-web-pgsql zabbix-apache-conf zabbix-sql-scripts zabbix-selinux-policy zabbix-agent 
```

## install Portainer 
```shell
docker volume create portainer_data
docker run -d -p 32125:8000 -p 32126:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock \
 -v portainer_data:/data portainer/portainer-ce:2.27.0-alpine
```

## Create initial database 
```shell

```