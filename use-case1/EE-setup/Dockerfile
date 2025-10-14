# Base : utiliser une image CentOS 7 minimaliste
FROM centos:7


RUN sed -i 's/mirror.centos.org/vault.centos.org/g' /etc/yum.repos.d/*.repo \
    && sed -i 's/^#.*baseurl=http/baseurl=http/g' /etc/yum.repos.d/*.repo \
    && sed -i 's/^mirrorlist=http/#mirrorlist=http/g' /etc/yum.repos.d/*.repo

# Installer les dépendances système nécessaires
RUN yum install -y \
    python \
    python-devel \
    python-pip \
    gcc \
    git \
    sudo \
    which \
    tar \
    bzip2 \
    shadow-utils \
    && yum clean all

RUN yum groupinstall -y "Development tools"

RUN /usr/bin/python -m pip install --upgrade \
    pip==20.3.4 \
    setuptools==44.1.1


# S'assurer que 'pip' utilise la bonne version de Python (Python 2.7.5 est le Python par défaut sur CentOS 7)
RUN pip install --upgrade pip

# Installer les dépendances de ansible-builder (non nécessaire pour l'exécution, mais bonne pratique)
# et les outils d'Ansible Runner
RUN pip install "ansible-runner"

# --- Préparation pour Ansible 2.9.13 ---
# Ansible 2.9.13 sera installé dans requirements.txt

# Créer un répertoire de travail
WORKDIR /usr/local/bin

# Définir l'utilisateur d'exécution pour AWX (par défaut : 1000)
# AWX/Ansible Automation Platform exécute les travaux en tant qu'utilisateur non root.
RUN groupadd -r ansible && useradd -r -g ansible -u 1000 ansible

# Définir l'utilisateur par défaut dans l'image
USER 1000

# Définir des variables d'environnement importantes
ENV ANSIBLE_PYTHON_INTERPRETER="/usr/bin/python"
ENV PATH="/usr/local/bin:$PATH"

# (Vous construirez l'image avec `ansible-builder build`)
# L'étape finale d'installation d'Ansible se fait via requirements.txt