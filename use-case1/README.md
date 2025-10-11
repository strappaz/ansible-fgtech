# Use-case 1

Gérer les différentes versions d'Ansible, de Python (2 et 3), et de leurs modules sur des systèmes d'exploitation (OS) 
vieillissants est un défi d'automatisation courant et complexe qui nécessite une stratégie à 
deux niveaux : Contrôle (où Ansible s'exécute) et Cible (où les Playbooks s'appliquent).

Voici comment gérer cette complexité de manière efficace, en utilisant les outils standards de la communauté Ansible et 
les meilleures pratiques pour les environnements de production (AWX/AAP).

## Gestion des Versions du Nœud de Contrôle (Ansible et son Python)

### Solution de Développement et Test : Tox (ou Environnements Virtuels Python)
Pour les développeurs testant la compatibilité de leurs rôles avec diverses versions d'Ansible (ex: 2.9, 2.12, 2.19) :

* Tox : C'est l'outil le plus efficace. Il permet de définir un fichier de configuration (tox.ini) qui crée et exécute 
automatiquement des tests dans plusieurs environnements virtuels Python isolés (appelés testenv).
Chaque environnement virtuel installe une version spécifique d'Ansible Core et ses dépendances.
Cela garantit que votre code fonctionne correctement, que vous l'exécutiez avec Ansible 2.9 (supportant Python 2 sur 
la cible) ou Ansible 2.19.3 (plus récent avec Python 3.13).