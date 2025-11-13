# Install Zabbix

## install on Almalinux 9 
```shell
sudo vi /etc/yum.repos.d/epel.repo # in epel add  excludepkgs=zabbix*
sudo rpm -Uvh https://repo.zabbix.com/zabbix/7.4/release/alma/9/noarch/zabbix-release-latest-7.4.el9.noarch.rpm
sudo dnf clean all
sudo dnf install -y zabbix-server-pgsql zabbix-web-pgsql zabbix-apache-conf zabbix-sql-scripts zabbix-selinux-policy zabbix-agent
sudo dnf update -y
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo dnf install -y postgresql16-server
sudo /usr/pgsql-16/bin/postgresql-16-setup initdb
sudo systemctl enable postgresql-16
sudo systemctl start postgresql-16
sudo -u postgres createuser --pwprompt zabbix
sudo -u postgres createdb -O zabbix zabbix
zcat /usr/share/zabbix/sql-scripts/postgresql/server.sql.gz | sudo -u zabbix psql zabbix
#Edit file /etc/zabbix/zabbix_server.conf
sudo systemctl restart zabbix-server zabbix-agent httpd php-fpm
sudo systemctl enable zabbix-server zabbix-agent httpd php-fpm
```

## Install zabbix-sender
```shell
sudo  rpm -Uvh https://repo.zabbix.com/zabbix/7.4/release/rhel/7/noarch/zabbix-release-latest-7.4.el7.noarch.rpm
sudo yum install -y zabbix-sender
rpm -q --filesbypkg zabbix-sender
```