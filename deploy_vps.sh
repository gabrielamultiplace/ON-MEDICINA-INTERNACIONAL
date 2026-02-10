#!/bin/bash
# ============================================
# Deploy - Plataforma ON Medicina Internacional
# VPS Ubuntu 22.04/24.04 - Hostinger
# ============================================

set -e

echo "=========================================="
echo " Plataforma ON - Deploy Automatizado"
echo "=========================================="

# Variáveis
APP_USER="onmedicina"
APP_DIR="/opt/onmedicina"
REPO_URL="https://github.com/gabrielamultiplace/ON-MEDICINA-INTERNACIONAL.git"
DOMAIN="app.onmedicinainternacional.com"

# 1. Atualizar sistema
echo ""
echo "[1/8] Atualizando sistema..."
apt update && apt upgrade -y

# 2. Instalar dependências
echo ""
echo "[2/8] Instalando dependências..."
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git ufw

# 3. Criar usuário da aplicação
echo ""
echo "[3/8] Configurando usuário..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    echo "Usuário $APP_USER criado"
else
    echo "Usuário $APP_USER já existe"
fi

# 4. Clonar/atualizar repositório
echo ""
echo "[4/8] Clonando repositório..."
if [ -d "$APP_DIR" ]; then
    cd $APP_DIR
    git pull origin main
    echo "Repositório atualizado"
else
    git clone $REPO_URL $APP_DIR
    echo "Repositório clonado"
fi

# 5. Configurar ambiente Python
echo ""
echo "[5/8] Configurando ambiente Python..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask gunicorn python-dotenv werkzeug requests

# Criar .env se não existir
if [ ! -f "$APP_DIR/.env" ]; then
    cat > $APP_DIR/.env << 'ENVEOF'
FLASK_ENV=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
ENVEOF
    echo ".env criado"
fi

# Criar diretórios necessários
mkdir -p $APP_DIR/data
mkdir -p $APP_DIR/uploads
mkdir -p $APP_DIR/Documentos

# Ajustar permissões
chown -R $APP_USER:$APP_USER $APP_DIR

# 6. Configurar Systemd
echo ""
echo "[6/8] Configurando serviço systemd..."
cat > /etc/systemd/system/onmedicina.service << 'SERVICEEOF'
[Unit]
Description=ON Medicina Internacional - Plataforma
After=network.target

[Service]
User=onmedicina
Group=onmedicina
WorkingDirectory=/opt/onmedicina
Environment="PATH=/opt/onmedicina/venv/bin"
ExecStart=/opt/onmedicina/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 120 --access-logfile /opt/onmedicina/access.log --error-logfile /opt/onmedicina/error.log app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable onmedicina
systemctl restart onmedicina
echo "Serviço onmedicina configurado e iniciado"

# 7. Configurar Nginx
echo ""
echo "[7/8] Configurando Nginx..."
cat > /etc/nginx/sites-available/onmedicina << NGINXEOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 50M;

    # Headers anti-cache para desenvolvimento
    add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;
    add_header Pragma "no-cache" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }

    location /uploads/ {
        alias /opt/onmedicina/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

# Ativar site
ln -sf /etc/nginx/sites-available/onmedicina /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar e recarregar Nginx
nginx -t
systemctl reload nginx
echo "Nginx configurado"

# 8. Configurar Firewall
echo ""
echo "[8/8] Configurando firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
echo "Firewall configurado"

echo ""
echo "=========================================="
echo " Deploy Concluído!"
echo "=========================================="
echo ""
echo " Acesse: http://$DOMAIN"
echo ""
echo " Para SSL (HTTPS), execute:"
echo "   certbot --nginx -d $DOMAIN"
echo ""
echo " Comandos úteis:"
echo "   systemctl status onmedicina    - Ver status"
echo "   systemctl restart onmedicina   - Reiniciar app"
echo "   journalctl -u onmedicina -f    - Ver logs em tempo real"
echo "   tail -f /opt/onmedicina/error.log - Logs de erro"
echo ""
