#!/usr/bin/env python3
"""Deploy script - executes steps 5-8 on VPS via SSH"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('69.62.91.8', username='root', password='@Omedicina2025', timeout=15)

def run(cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out)
    if err and 'WARNING' not in err.upper(): print('STDERR:', err[-300:])
    return out

# Step 5: Create .env
print('=== [5/8] Criando .env ===')
run("""
cd /opt/onmedicina
SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$SECRET
EOF
echo '.env criado'
mkdir -p data uploads Documentos
chown -R onmedicina:onmedicina /opt/onmedicina
echo 'Permissoes OK'
""")

# Step 6: Create systemd service
print('=== [6/8] Configurando systemd ===')
service_content = """[Unit]
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
"""

sftp = ssh.open_sftp()
with sftp.open('/etc/systemd/system/onmedicina.service', 'w') as f:
    f.write(service_content)
sftp.close()

run('systemctl daemon-reload && systemctl enable onmedicina && systemctl restart onmedicina')
import time; time.sleep(3)
print(run('systemctl status onmedicina --no-pager -l | head -15'))

# Step 7: Configure Nginx
print('=== [7/8] Configurando Nginx ===')
nginx_conf = """server {
    listen 80;
    server_name app.onmedicinainternacional.com 69.62.91.8;

    client_max_body_size 50M;

    add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;
    add_header Pragma "no-cache" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }

    location /uploads/ {
        alias /opt/onmedicina/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
"""

sftp2 = ssh.open_sftp()
with sftp2.open('/etc/nginx/sites-available/onmedicina', 'w') as f:
    f.write(nginx_conf)
sftp2.close()

run("""
ln -sf /etc/nginx/sites-available/onmedicina /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t 2>&1
systemctl reload nginx
echo 'Nginx OK'
""")

# Step 8: Firewall
print('=== [8/8] Configurando firewall ===')
run("""
ufw allow OpenSSH
ufw allow 'Nginx Full'
echo 'y' | ufw enable 2>/dev/null || true
ufw status
""")

# Test
print('=== TESTE FINAL ===')
result = run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000/")
print('HTTP Status:', result)

ssh.close()
print('\nDEPLOY CONCLUIDO!')
