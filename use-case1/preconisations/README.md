# Preconisations Example 1
Le besoin d'assurer la compatibilité du code développé sur une batterie d'OS hétérogènes (y compris les anciens avec Python 2.7) est l'objectif principal de la **stratégie de test DevOps** pour la gestion de la dette technique.

;:q
Pour ce faire, **l'utilisation des Execution Environments (EE) AWX est essentielle**, et l'intégration d'un framework de test comme **Molecule** est hautement recommandée.

---

## **1\. Utilité des Outils et Choix Stratégiques 💡**

| Outil | Utilité | Justification du Choix |
| :---- | :---- | :---- |
| **EE AWX (Execution Environment)** | **Oui.** Isole l'environnement de contrôle (Ansible/Python/Dépendances) du système d'exploitation hôte. | **Obligatoire.** C'est le seul moyen stable d'utiliser Ansible 2.9.x et ses modules spécifiques sans casser la plateforme AWX. |
| **Molecule** | **Oui.** Framework de test unitaire et d'intégration pour les rôles Ansible. | **Recommandé.** Permet de définir des scénarios de test (vérification des services, des fichiers, des versions) sur différentes plateformes (Docker, Vagrant). |
| **Tox** | Non directement. | Principalement pour les tests Python. L'approche de Molecule, qui utilise les conteneurs, est plus pertinente pour les tests d'infrastructure. |

La stratégie repose sur **Molecule** pour le développement/test unitaire local, et **AWX/EE** pour l'exécution et la validation en environnement intégré.

---

## **2\. Structure du Projet Git et Définition de l'Inventaire 📂**

La structure du projet doit respecter les standards d'Ansible et isoler clairement les configurations entre les environnements et les rôles.

### **A. Structure du Dépôt Git**

Le dépôt unique (monorepo) est la meilleure approche pour les rôles et playbooks.

/mon\_projet\_ansible  
├── ansible.cfg                    \# Configuration générale  
├── inventory/  
│   ├── dev/  
│   │   ├── hosts.yml              \# Hôtes dev  
│   │   └── group\_vars/  
│   │       └── all.yml            \# Variables spécifiques dev (ansible\_python\_interpreter: /usr/bin/python3, etc.)  
│   ├── staging/  
│   │   ├── hosts.yml              \# Hôtes staging  
│   │   └── group\_vars/  
│   │       └── all.yml            \# Variables staging  
│   └── prod/  
│       ├── hosts.yml              \# Hôtes production  
│       └── group\_vars/  
│           └── all.yml            \# Variables prod  
├── playbooks/  
│   └── main\_deploy.yml            \# Playbook d'entrée pour le déploiement  
└── roles/  
    └── common\_security/           \# Rôle pour la sécurité de base  
    │   ├── tasks/  
    │   │   └── main.yml  
    │   └── molecule/              \# Structure pour les tests Molecule  
    │       └── default/  
    │           └── converge.yml   \# Playbook de test local Molecule  
    └── legacy\_app\_deploy/         \# Rôle pour l'application héritée  
        ├── tasks/  
        └── molecule/  
            └── centos7-test/      \# Scénario spécifique pour Python 2.7/CentOS 7  
                └── molecule.yml

### **B. Définition des Inventaires (group\_vars)**

La gestion des interpréteurs Python est faite au niveau du groupe all dans chaque environnement pour garantir la compatibilité des hôtes cibles.

| Environnement | Fichier de Variables | Définition de l'Interpréteur Python |
| :---- | :---- | :---- |
| **Production** | inventory/prod/group\_vars/all.yml | ansible\_python\_interpreter: /usr/bin/python |
| **Staging** | inventory/staging/group\_vars/all.yml | ansible\_python\_interpreter: /usr/libexec/platform-python (RHEL/AlmaLinux 8+) |
| **Développement** | inventory/dev/group\_vars/all.yml | ansible\_python\_interpreter: /usr/bin/python3 |

---

## **3\. Mise en Place des Actions Ansible et AWX**

Le processus de garantie de compatibilité se déroule en trois étapes distinctes.

### **A. Phase 1 : Tests Unitaires Locaux (Molecule)**

**Objectif :** Valider la logique des rôles contre les systèmes cibles hétérogènes (y compris l'ancienne pile Python).

1. **Configuration Molecule :** Dans le scénario de test Molecule (roles/legacy\_app\_deploy/molecule/centos7-test/molecule.yml), configurez l'utilisation de l'image **centos:7** et forcez l'interpréteur :  
   YAML  
   \# Configuration du scénario Molecule pour CentOS 7  
   driver:  
     name: docker  
   platforms:  
     \- name: centos7-py2  
       image: centos:7  
       command: /usr/sbin/init  
       \# Utiliser l'interpréteur Python 2.7 du système cible  
       ansible\_python\_interpreter: /usr/bin/python

2. **Exécution Locale :** Les développeurs exécutent le test avant le *merge* :  
   Bash  
   molecule test \-s centos7-test

### **B. Phase 2 : Levier AWX pour la Compatibilité Ansible/Python**

**Objectif :** Exécuter le Playbook dans un environnement de contrôle stable (EE Python 3\) tout en ciblant les hôtes anciens (Python 2.7).

1. **Création des Execution Environments (EE) :**  
   * **EE Principal (Stable) :** EE basé sur Python 3 (pour ansible-runner stable) contenant **Ansible 2.9.27**. C'est le mon-ee-29-py3-final:latest que nous avons construit, qui gère la dette technique.  
   * **EE Moderne :** EE basé sur Python 3 contenant la version d'Ansible la plus récente (ex: Ansible 8.x) pour les cibles modernes.  
2. **Configuration du Job Template AWX :**  
   * Créez un Job Template pour le déploiement sur Production (prod-deploy).  
   * Sélectionnez l'inventaire **prod**.  
   * Sélectionnez l'Execution Environment **EE Principal (Ansible 2.9.27)**.

### **C. Phase 3 : Assurer l'Exécution des Modules (Actions Ansible)**

Dans le Playbook, l'action Ansible clé pour la compatibilité avec les systèmes anciens est le module pip (si nécessaire) et la gestion de ANSIBLE\_PYTHON\_INTERPRETER.

**Playbook d'Exécution (Déploiement) :**

YAML

\# playbooks/main\_deploy.yml  
\---  
\- name: Séquence de déploiement sécurisée  
  hosts: all  
  gather\_facts: no  
    
  pre\_tasks:  
    \- name: DEBUG \- Afficher l'interpréteur pour validation  
      ansible.builtin.debug:  
        msg: "Connexion vers {{ inventory\_hostname }} via {{ ansible\_python\_interpreter }}"

  roles:  
    \- common\_security  \# S'exécute sur tous les hôtes  
    \- legacy\_app\_deploy \# S'exécute uniquement là où c'est nécessaire

  post\_tasks:  
    \- name: Redémarrer le service (exemple)  
      ansible.builtin.service:  
        name: legacy\_app  
        state: restarted  
      when: legacy\_app\_deploy\_result is changed  



