# Use-case 1

Gérer les différentes versions d'Ansible, de Python (2 et 3), et de leurs modules sur des systèmes d'exploitation (OS) 
vieillissants est un défi d'automatisation courant et complexe qui nécessite une stratégie à 
deux niveaux : Contrôle (où Ansible s'exécute) et Cible (où les Playbooks s'appliquent).

Voici comment gérer cette complexité de manière efficace, en utilisant les outils standards de la communauté Ansible et 
les meilleures pratiques pour les environnements de production (AWX/AAP).

## Gestion des Versions du Nœud de Contrôle (Ansible et son Python)

### Solution  basiqe de Développement et de Test : Tox (ou Environnements Virtuels Python)
Pour les développeurs testant la compatibilité de leurs rôles avec diverses versions d'Ansible (ex: 2.9, 2.12, 2.19) :

* Tox : C'est l'outil le plus connu. Il permet de définir un fichier de configuration (tox.ini) qui crée et exécute 
automatiquement des tests dans plusieurs environnements virtuels Python isolés (appelés testenv).
Chaque environnement virtuel installe une version spécifique d'Ansible Core et ses dépendances.
Cela garantit que votre code fonctionne correctement, que vous l'exécutiez avec Ansible 2.9 (supportant Python 2 sur 
la cible) ou Ansible 2.19.3 (plus récent avec Python 3.13).

### Solution avec Ansible AWX
La méthode standard et recommandée pour gérer plusieurs versions d'Ansible dans AWX sous Kubernetes est d'utiliser des 
Environnements d'Exécution (Execution Environments - EE) personnalisés.

Un Execution Environment est une image de conteneur qui contient l'ensemble des dépendances nécessaires pour exécuter 
les playbooks Ansible, y compris une version spécifique d'ansible-core, des collections Ansible, des modules Python, 
et des dépendances au niveau du système d'exploitation.

Puisque AWX s'exécute sur Kubernetes, chaque tâche d'automatisation s'exécute dans un conteneur (Pod) basé sur une 
image d'Execution Environment. Pour utiliser différentes versions d'Ansible, vous devez construire vos 
propres images d'EE.

### Exemple 
Target version of centos is 2009   (/09/2020) 
ansible version is v2.9.13 (1/09/2020)
python3  is 3.5.10 (05/09/2020)
python  is 2.7.5