#!/bin/bash
# ============================================
# Atualizar Plataforma ON na VPS
# Execute: sudo bash atualizar_vps.sh
# ============================================

set -e

APP_DIR="/opt/onmedicina"

echo "Atualizando Plataforma ON..."

cd $APP_DIR

# Puxar atualizações do GitHub
git pull origin main

# Atualizar dependências se necessário
source venv/bin/activate
pip install -r requirements.txt 2>/dev/null || true

# Ajustar permissões
chown -R onmedicina:onmedicina $APP_DIR

# Reiniciar serviço
systemctl restart onmedicina

echo ""
echo "✅ Atualização concluída!"
echo ""
systemctl status onmedicina --no-pager -l | head -15
