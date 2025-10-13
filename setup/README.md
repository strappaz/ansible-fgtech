# install environment

## Configuration de sysctl
```shell
  cd /home/alma/ansible-fgtech
  echo  vm.max_map_count=262144 | sudo tee -a /etc/sysctl.conf
  echo fs.inotify.max_user_watches=655360 | sudo tee -a /etc/sysctl.conf
  echo fs.inotify.max_user_instances=1280 | sudo tee -a /etc/sysctl.conf
  echo fs.file-max = 2097152 | sudo tee -a /etc/sysctl.conf
  sudo sysctl -p
```

## Check 
```shell
ANSIBLE_PYTHON_INTERPRETER=auto_silent ansible all  -m ping -i inventory 
```

## Caveats
```shell
ansible-config list  # list all configurations
ansible-config view  # Shows the current config file
ansible-config dump  # Shows the current settings
```