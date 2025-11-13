# Packages
25 hôtes almalinux 10 doivent etre identifiés dans un groupe d'inventaire spécifique, 
par exemple alma10_servers.

## Build almalinux image
```shell
cd ~/ansible-fgtech
export DISTR='almalinux'
export VERSION='10'
export KEY_CONTENT=$(cat ~/.ssh/id_rsa.pub)
docker build --build-arg SSH_PUBLIC_KEY="${KEY_CONTENT}" \
-t docker-systemd:${DISTR}-${VERSION} -f ${DISTR}/${VERSION}.Dockerfile .
```

## Creer 25 containers almalinux 10
### Definition du groupe cible
sudo cp /etc/hosts /etc/hosts.bck
cd setup  
execute ```sudo python3 generate_almalinux.py```   
ce script met a jour le fichier /etc/hosts  
voir le fichier inventory   
check  ```ansible alma10_servers  -m ping -i inventory```    


### Execution de reference sans fork fork = 5
```shell
ansible-playbook playbook.yml -i inventory -f 5
```
Notez le resultat exemple 1.25 pour fork 5  

### Execution de reference  fork = 15
```shell
sudo cp /etc/hosts.bck /etc/hosts
# delete all alma containers using portainer
# execute sudo python3 generate_almalinux.py 
ansible-playbook playbook.yml -i inventory -f 15
```
Check hosts et execute docker ps  
Notez le resultat exemple 2.41 pour fork 15   

### Execution de reference  fork = 25
```shell
sudo cp /etc/hosts.bck /etc/hosts
# delete all alma containers using portainer
# execute sudo python3 generate_almalinux.py 
ansible-playbook playbook.yml -i inventory -f 25
```
Check hosts et execute docker ps  
Notez le resultat exemple 2.17 pour fork 25   


### Execution de reference avec serial 5  fork = 25
```shell
sudo cp /etc/hosts.bck /etc/hosts
# delete all alma containers using portainer
# execute sudo python3 generate_almalinux.py 
ansible-playbook serial.yml -i inventory -f 25
```
Check hosts et execute docker ps  
Notez le resultat exemple 5.04 pour serial 5 et  fork 25     
evite la saturation du controlleur en prod

### Execution de reference avec async :600 poll 5
L'exécution asynchrone permet à Ansible de lancer la tâche et de ne   
la vérifier que plus tard, libérant ainsi le nœud de contrôle.

```shell
sudo cp /etc/hosts.bck /etc/hosts
# delete all alma containers using portainer
# execute sudo python3 generate_almalinux.py 
ansible-playbook async.yml -i inventory -f 25
```
Check hosts et execute docker ps  
Notez le resultat exemple 3:25 pour serial 5 et  fork 25     
evite la saturation du controlleur en prod 

### Execution de reference avec async :600 poll 0
poll = 0 laisse le controlleur effectuer la tache sur tous les hosts sans controle
```shell
sudo cp /etc/hosts.bck /etc/hosts
# delete all alma containers using portainer
# execute sudo python3 generate_almalinux.py 
ansible-playbook poll_zero.yml -i inventory -f 25
```
Check hosts et execute docker ps  
Notez le resultat exemple 0:34 pour async:600 poll 0  

### Execution de reference avec throttle : 3
throttle est utilisé pour limiter le nombre d'hôtes qui exécutent  
une tâche spécifique en même temps, indépendamment des forks globaux.
