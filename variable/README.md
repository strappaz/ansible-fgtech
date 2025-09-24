Les variables Ansible sont des conteneurs qui stockent des valeurs. Leur rôle principal est de rendre les playbooks **dynamiques, flexibles et réutilisables** en séparant les données de la logique des tâches.

Elles permettent de gérer des valeurs qui peuvent changer en fonction du contexte, comme les environnements (développement, production), les noms d'hôtes ou les versions de logiciels.

-----

## Les Rôles Clés des Variables 🔑

#### 1\. Rendre les Playbooks Réutilisables

Plutôt que d'écrire une valeur en dur (par exemple, un nom de paquet comme `apache2`), vous utilisez une variable (ex: `web_package`). Vous pouvez ensuite réutiliser ce playbook pour installer un autre serveur web (comme `nginx`) simplement en changeant la valeur de la variable, sans modifier les tâches elles-mêmes.

#### 2\. Gérer les Différences entre les Environnements

Les informations de connexion à une base de données ne sont pas les mêmes en développement et en production. Les variables permettent de charger le bon fichier de configuration (`dev_vars.yml` ou `prod_vars.yml`) en fonction de l'environnement cible, rendant le playbook adaptable.

#### 3\. Simplifier les Données Complexes

Les variables peuvent contenir des listes (ex: une liste d'utilisateurs à créer) ou des dictionnaires (ex: les détails de configuration d'une application). Cela permet de structurer les données de manière claire et de les parcourir avec des boucles (`loop`) dans vos tâches.

#### 4\. Sécuriser les Informations Sensibles (Secrets)

Avec **Ansible Vault**, vous pouvez chiffrer des fichiers de variables contenant des informations sensibles comme des mots de passe, des clés API ou des certificats SSL. Le playbook utilise la variable normalement, mais la valeur reste sécurisée et n'est pas visible en clair.

-----

## Comment et Où Définir les Variables ?

Ansible offre plusieurs endroits pour définir des variables, avec un système de priorité (précédence) pour décider quelle valeur utiliser si une variable est définie à plusieurs endroits.

Voici les méthodes les plus courantes, de la moins prioritaire à la plus prioritaire :

  * **Dans les rôles** (`roles/nom_du_role/defaults/main.yml` et `roles/nom_du_role/vars/main.yml`).
  * **Dans l'inventaire** : Pour définir des variables spécifiques à un groupe d'hôtes (`group_vars`) ou à un hôte unique (`host_vars`).
  * **Dans le Playbook lui-même** :
      * Via la section `vars` pour des variables locales au playbook.
      * Via la directive `vars_files` pour inclure des fichiers de variables externes.
  * **Via la sortie d'une tâche** : En utilisant le mot-clé `register` pour stocker le résultat d'une commande dans une variable.
  * **En ligne de commande** : En passant des variables avec l'option `-e` (pour "extra-vars") lors de l'exécution. C'est la méthode qui a la plus haute priorité.

-----

## Exemple Concret

Imaginez que vous deviez installer un serveur web et créer une page d'accueil. Sans variables, vous devriez tout écrire en dur. Avec des variables, le playbook devient plus abstrait et réutilisable.

```yaml
---
- name: Installer et configurer un serveur web
  hosts: webservers
  become: yes
  
  # Définition des variables directement dans le playbook
  vars:
    web_package: httpd      # Nom du paquet pour CentOS/RHEL
    service_name: httpd
    html_content: "Bienvenue sur notre site web !"

  tasks:
    - name: Installer le paquet du serveur web
      ansible.builtin.package:
        name: "{{ web_package }}"  # Utilisation de la variable ici
        state: present

    - name: Démarrer et activer le service web
      ansible.builtin.service:
        name: "{{ service_name }}"
        state: started
        enabled: yes

    - name: Créer une page d'accueil personnalisée
      ansible.builtin.copy:
        content: "{{ html_content }}"
        dest: /var/www/html/index.html
```

Dans cet exemple :

  * Si vous voulez déployer ce playbook sur des serveurs Debian/Ubuntu, il vous suffit de changer la valeur de `web_package` en `apache2` et `service_name` en `apache2` dans un fichier de variables pour ces hôtes, sans toucher à la logique des tâches.
  * Le contenu de la page d'accueil (`html_content`) est également externalisé, ce qui le rend facile à modifier.