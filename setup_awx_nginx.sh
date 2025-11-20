#!/bin/bash

# Script pour exposer AWX via nginx sur le port 443
# Usage: sudo ./setup_awx_nginx.sh <votre-domaine>
# Exemple: sudo ./setup_awx_nginx.sh student4.fedcloud.fr

set -e

if [ "$EUID" -ne 0 ]; then 
   echo "Ce script doit être exécuté avec sudo"
   exit 1
fi

if [ -z "$1" ]; then
    echo "Usage: $0 <votre-domaine>"
    echo "Exemple: $0 student4.fedcloud.fr"
    exit 1
fi

DOMAIN=$1
AWX_PORT=32001

echo "=== Configuration AWX + Nginx pour ${DOMAIN} ==="

# 1. Arrêter Portainer s'il utilise le port 443
echo "[1/6] Arrêt de Portainer..."
PORTAINER_CONTAINER=$(docker ps --filter "publish=443" --format "{{.ID}}" 2>/dev/null || true)
if [ -n "$PORTAINER_CONTAINER" ]; then
    echo "  → Arrêt du conteneur Portainer: $PORTAINER_CONTAINER"
    docker stop $PORTAINER_CONTAINER
else
    echo "  → Aucun conteneur sur le port 443"
fi

# 2. Arrêter les anciens port-forward kubectl
echo "[2/6] Arrêt des anciens port-forward kubectl..."
pkill -f "kubectl port-forward.*awx-demo-service" || true
sleep 2

# 3. Démarrer le port-forward kubectl sur le port 32001
echo "[3/6] Démarrage du port-forward kubectl (port ${AWX_PORT})..."
nohup kubectl port-forward -n awx service/awx-demo-service ${AWX_PORT}:80 --address='0.0.0.0' > /tmp/awx-portforward.log 2>&1 &
sleep 3

# Vérifier que le port-forward fonctionne
if ! ps aux | grep -v grep | grep "kubectl port-forward.*awx-demo-service" > /dev/null; then
    echo "  ✗ Erreur: kubectl port-forward n'a pas démarré"
    cat /tmp/awx-portforward.log
    exit 1
fi
echo "  ✓ kubectl port-forward actif sur le port ${AWX_PORT}"

# 4. Configurer nginx
echo "[4/6] Configuration de nginx..."
cat > /etc/nginx/conf.d/awx.conf << EOF
server {
       listen 443 ssl;
       ssl_certificate /etc/letsencrypt/live/${DOMAIN}/cert.pem;
       ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

       server_name ${DOMAIN};

       location / {
            proxy_pass http://127.0.0.1:${AWX_PORT}/;
            proxy_redirect http://127.0.0.1:${AWX_PORT}/ \$scheme://\$host/;
            proxy_http_version 1.1;
            proxy_read_timeout 20d;
       }
}
EOF

# 5. Tester et recharger nginx
echo "[5/6] Test et rechargement de nginx..."
nginx -t
if [ $? -ne 0 ]; then
    echo "  ✗ Erreur de configuration nginx"
    exit 1
fi
systemctl reload nginx
echo "  ✓ Nginx rechargé"

# 6. Configurer SELinux
echo "[6/6] Configuration de SELinux..."
setsebool -P httpd_can_network_connect 1
echo "  ✓ SELinux configuré"

echo ""
echo "=== Configuration terminée ==="
echo ""
echo "AWX est maintenant accessible sur:"
echo "  https://${DOMAIN}/"
echo ""
echo "Pour arrêter AWX:"
echo "  sudo pkill -f 'kubectl port-forward.*awx-demo-service'"
echo ""
echo "Pour vérifier le port-forward:"
echo "  ps aux | grep 'kubectl port-forward' | grep -v grep"
echo ""

