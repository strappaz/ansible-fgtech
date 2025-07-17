Absolument. C'est une excellente démarche pour professionnaliser la gestion de votre infrastructure d'automatisation. Monitorer AWX avec Grafana vous permet de passer d'une gestion réactive ("un utilisateur se plaint que son job est lent") à une gestion proactive ("je vois que la file d'attente s'allonge, je dois investiguer avant que cela ne devienne un problème").

Voici un guide complet qui vous montrera comment :
1.  Mettre en place la pile de monitoring (Grafana + Prometheus) dans Docker.
2.  Configurer Prometheus pour qu'il collecte les métriques d'AWX.
3.  Configurer Grafana et créer des tableaux de bord avec des cas d'usage concrets et des KPI pertinents.

---

### Architecture de la Solution

Nous allons utiliser la pile standard pour ce type de monitoring :

*   **AWX** : L'application que nous voulons monitorer. Elle expose nativement ses métriques au format Prometheus sur un endpoint spécifique.
*   **Prometheus** : Un système de monitoring et d'alerting qui va "scraper" (collecter périodiquement) les métriques d'AWX et les stocker dans sa base de données temporelle.
*   **Grafana** : Un outil de visualisation qui va se connecter à Prometheus comme source de données (`Data Source`) pour créer des tableaux de bord dynamiques et interactifs.

Le tout sera orchestré avec Docker Compose pour une mise en place simple et reproductible.

### Prérequis

*   Une instance d'Ansible AWX fonctionnelle.
*   Docker et Docker Compose installés sur une machine qui peut communiquer avec votre instance AWX.
*   Un accès administrateur à AWX pour générer un token d'authentification.

---

### Étape 1 : Mise en Place de la Pile Grafana + Prometheus

1.  **Créez un répertoire de travail** pour votre projet de monitoring.
    ```bash
    mkdir awx-monitoring
    cd awx-monitoring
    ```

2.  **Générez un Token d'Application dans AWX**
    Prometheus a besoin de s'authentifier pour accéder à l'endpoint des métriques (`/api/v2/metrics`). Il est fortement recommandé de créer un token d'application dédié plutôt que d'utiliser un token personnel.

    *   Dans l'interface AWX, allez dans **Administration -> Applications**.
    *   Cliquez sur **Ajouter**.
    *   **Nom** : `Prometheus Scraper`
    *   **Organisation** : (Choisissez une organisation pertinente)
    *   **Type d'autorisation** : `Génération de code d'autorisation`
    *   **URI de redirection** : Mettez une URL factice comme `http://localhost`
    *   **Type de client** : `Confidentiel`
    *   Sauvegardez. **NE FERMEZ PAS LA FENÊTRE.** Copiez immédiatement le **TOKEN D'ACCÈS PERSONNEL** qui s'affiche. Il ne sera plus jamais visible. Stockez-le précieusement.

3.  **Créez le fichier de configuration de Prometheus (`prometheus.yml`)**
    Ce fichier indique à Prometheus quelles cibles il doit surveiller.

    ```yaml
    # awx-monitoring/prometheus.yml

    global:
      scrape_interval: 15s # Collecter les données toutes les 15 secondes

    scrape_configs:
      - job_name: 'awx'
        bearer_token: 'VOTRE_TOKEN_AWX_COLLE_ICI' # Remplacez par le token généré à l'étape 2
        metrics_path: /api/v2/metrics
        scheme: http # ou https si votre AWX utilise TLS
        static_configs:
          - targets: ['VOTRE_IP_OU_HOSTNAME_AWX:PORT'] # Ex: '192.168.1.50' ou 'awx.mondomaine.com'

        # Si votre AWX utilise un certificat auto-signé, décommentez la ligne suivante.
        # ATTENTION: A n'utiliser qu'en environnement de test.
        # tls_config:
        #   insecure_skip_verify: true
    ```

4.  **Créez le fichier `docker-compose.yml`**
    Ce fichier va définir et lancer nos deux conteneurs : Prometheus et Grafana.

    ```yaml
    # awx-monitoring/docker-compose.yml

    version: '3.7'

    services:
      prometheus:
        image: prom/prometheus:latest
        container_name: prometheus
        ports:
          - "9090:9090"
        volumes:
          - ./prometheus.yml:/etc/prometheus/prometheus.yml
          - prometheus_data:/prometheus
        command:
          - '--config.file=/etc/prometheus/prometheus.yml'
        restart: unless-stopped

      grafana:
        image: grafana/grafana:latest
        container_name: grafana
        ports:
          - "3000:3000"
        volumes:
          - grafana_data:/var/lib/grafana
        restart: unless-stopped

    volumes:
      prometheus_data: {}
      grafana_data: {}
    ```

5.  **Lancez les conteneurs**
    ```bash
    docker-compose up -d
    ```

6.  **Vérifiez que tout fonctionne**
    *   **Prometheus** : Ouvrez `http://<VOTRE_IP>:9090`. Allez dans **Status -> Targets**. Vous devriez voir votre cible `awx` avec un état "UP" (en vert).
    *   **Grafana** : Ouvrez `http://<VOTRE_IP>:3000`. Connectez-vous avec `admin` / `admin`. Il vous sera demandé de changer le mot de passe.

---

### Étape 2 : Configuration de Grafana

1.  **Ajouter Prometheus comme source de données**
    *   Dans l'interface Grafana, allez dans le menu de gauche **Configuration (roue crantée) -> Data Sources**.
    *   Cliquez sur **Add data source**.
    *   Choisissez **Prometheus**.
    *   Dans le champ **URL**, entrez `http://prometheus:9090`. Nous pouvons utiliser le nom de service `prometheus` car les conteneurs sont dans le même réseau Docker Compose.
    *   Cliquez sur **Save & test**. Vous devriez voir un message vert "Data source is working".

Vous êtes maintenant prêt à créer des visualisations !

---

### Étape 3 : Cas Concrets de Monitoring et KPI pour AWX

Voici des exemples de tableaux de bord et de panneaux que vous pouvez créer pour obtenir des informations précieuses. Allez dans **Dashboards -> New dashboard -> Add new panel**.

#### Cas 1 : Santé Générale des Jobs (Vue d'ensemble)

*   **KPI** : Nombre de jobs par statut (Succès, Échec, En cours, En attente).
*   **Pourquoi c'est important** : Donne une vision instantanée de la santé de votre automatisation. Une augmentation soudaine des échecs est un signal d'alerte immédiat.
*   **Visualisation** : Panneaux "Stat" ou "Pie chart".

**Requêtes PromQL (une par panneau Stat) :**
*   **En cours (Running)** : `awx_running_jobs`
*   **En attente (Pending)** : `awx_pending_jobs`
*   **Total Échecs (depuis le dernier redémarrage)** : `awx_jobs_total{status="failed"}`
*   **Total Succès (depuis le dernier redémarrage)** : `awx_jobs_total{status="successful"}`



#### Cas 2 : Taux d'Échec des Jobs

*   **KPI** : Pourcentage ou nombre d'échecs sur les 5 dernières minutes.
*   **Pourquoi c'est important** : Identifie les instabilités. Un taux d'échec élevé peut indiquer un problème avec un playbook, des identifiants invalides, ou une connectivité réseau défaillante.
*   **Visualisation** : "Graph".

**Requête PromQL :**
```promql
// Taux d'échecs par seconde, moyenné sur 5 minutes
rate(awx_jobs_total{status="failed"}[5m])
```

#### Cas 3 : Performance des Jobs (Durée d'exécution)

*   **KPI** : Durée moyenne d'exécution des jobs.
*   **Pourquoi c'est important** : Détecte les régressions de performance. Si un job qui prenait 2 minutes en prend soudainement 10, il faut enquêter.
*   **Visualisation** : "Graph" ou "Heatmap" (pour voir la distribution).

**Requête PromQL :**
```promql
// Durée moyenne d'exécution des jobs sur les 5 dernières minutes
// On divise la somme des durées par le nombre de jobs terminés
rate(awx_job_elapsed_seconds_sum[5m]) / rate(awx_job_elapsed_seconds_count[5m])
```
Vous pouvez aussi filtrer par template de job :
```promql
// Durée moyenne pour un template de job spécifique
rate(awx_job_elapsed_seconds_sum{job_template_name="Deploy App Server"}[5m]) / rate(awx_job_elapsed_seconds_count{job_template_name="Deploy App Server"}[5m])
```

#### Cas 4 : Charge du Système et Temps d'Attente

*   **KPI** : Nombre de jobs dans la file d'attente (`pending`).
*   **Pourquoi c'est important** : C'est le meilleur indicateur de la saturation de votre instance AWX. Si le nombre de jobs en attente augmente constamment, cela signifie que vous soumettez plus de jobs que ce que AWX ne peut en exécuter. Il faut peut-être augmenter la capacité (forks) ou optimiser les playbooks.
*   **Visualisation** : "Graph" ou "Gauge".

**Requête PromQL :**
```promql
// Nombre de jobs actuellement en attente
awx_pending_jobs
```



#### Cas 5 : Utilisation de la Capacité

*   **KPI** : Pourcentage de la capacité (forks) utilisée.
*   **Pourquoi c'est important** : Permet de planifier la capacité. AWX a une limite sur le nombre total de processus parallèles (`forks`) qu'il peut lancer. Ce KPI vous montre à quel point vous vous approchez de cette limite.
*   **Visualisation** : "Gauge".

**Requête PromQL :**
```promql
# Pourcentage de la capacité utilisée
# (capacité consommée / capacité totale) * 100
(sum(awx_capacity) / sum(awx_instance_capacity)) * 100
```

### Conseil de Pro : Utiliser un Dashboard Communautaire

Plutôt que de tout recréer, vous pouvez importer un tableau de bord déjà fait par la communauté.
1.  Allez sur le site [Grafana Dashboards](https://grafana.com/grafana/dashboards/).
2.  Cherchez "AWX". Un tableau de bord populaire est [**AWX Dashboard (ID: 10433)**](https://grafana.com/grafana/dashboards/10433-awx-dashboard/).
3.  Copiez l'ID (`10433`).
4.  Dans votre Grafana, allez dans **Dashboards -> Import**.
5.  Collez l'ID dans le champ "Import via grafana.com" et cliquez sur **Load**.
6.  Choisissez votre source de données Prometheus et cliquez sur **Import**.

Vous aurez instantanément un tableau de bord complet que vous pourrez ensuite personnaliser selon vos besoins.