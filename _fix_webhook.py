#!/usr/bin/env python3
"""Fix webhook: add SSL to nginx + deploy route fix"""
import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('69.62.91.8', username='root', password='@Omedicina2025', timeout=15)

def run(cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err and 'warning' not in err.lower(): print('ERR:', err[-500:])
    return out

# 1. Check existing SSL certs
print('=== 1. SSL Certs ===')
run('ls /etc/letsencrypt/live/app.onmedicinainternacional.com/ 2>/dev/null')
run('ls /etc/nginx/ssl/ 2>/dev/null')

# 2. Check which cert files exist and are valid
print('\n=== 2. Cert validity ===')
run('openssl x509 -in /etc/letsencrypt/live/app.onmedicinainternacional.com/fullchain.pem -noout -dates 2>/dev/null || echo LETSENCRYPT_CERT_MISSING')
run('openssl x509 -in /etc/nginx/ssl/fullchain.pem -noout -dates 2>/dev/null || echo NGINX_SSL_CERT_MISSING')

# 3. Write new nginx config with SSL
print('\n=== 3. Writing nginx config with SSL ===')
nginx_config = """server {
    listen 80;
    server_name app.onmedicinainternacional.com 69.62.91.8;
    
    # Redirect HTTP to HTTPS for the domain
    if ($host = app.onmedicinainternacional.com) {
        return 301 https://$host$request_uri;
    }

    # Allow direct IP access on port 80
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

server {
    listen 443 ssl;
    server_name app.onmedicinainternacional.com;

    ssl_certificate /etc/letsencrypt/live/app.onmedicinainternacional.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.onmedicinainternacional.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 50M;

    add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;
    add_header Pragma "no-cache" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
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

# Write config
cmd_write = "cat > /etc/nginx/sites-available/onmedicina << 'NGINXEOF'\n" + nginx_config + "NGINXEOF"
run(cmd_write)

# 4. Test nginx config
print('\n=== 4. Test nginx config ===')
result = run('nginx -t 2>&1')

# If Let's Encrypt cert doesn't work, try the /etc/nginx/ssl/ cert
if 'failed' in result.lower() or 'error' in result.lower():
    print('\nLet\'s Encrypt cert failed, trying /etc/nginx/ssl/ cert...')
    nginx_config2 = nginx_config.replace(
        '/etc/letsencrypt/live/app.onmedicinainternacional.com/fullchain.pem',
        '/etc/nginx/ssl/fullchain.pem'
    ).replace(
        '/etc/letsencrypt/live/app.onmedicinainternacional.com/privkey.pem',
        '/etc/nginx/ssl/privkey.pem'
    )
    cmd_write2 = "cat > /etc/nginx/sites-available/onmedicina << 'NGINXEOF'\n" + nginx_config2 + "NGINXEOF"
    run(cmd_write2)
    result = run('nginx -t 2>&1')

print('\n=== 5. Reload nginx ===')
if 'successful' in result.lower() or 'ok' in result.lower():
    run('systemctl reload nginx')
    print('Nginx reloaded')
else:
    print('SKIPPING reload - nginx config has errors')

# 6. Git pull + restart app
print('\n=== 6. Git pull + restart ===')
run('cd /opt/onmedicina && git pull origin main')
run('systemctl restart onmedicina')
time.sleep(3)

# 7. Test webhook endpoint locally
print('\n=== 7. Test webhook endpoint ===')
code1 = run("curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:5000/comercial/webhooks -H 'Content-Type: application/json' -d '{\"event\":\"test\"}'")
print('POST /comercial/webhooks:', code1)

code2 = run("curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:5000/api/asaas/webhook -H 'Content-Type: application/json' -d '{\"event\":\"test\"}'")
print('POST /api/asaas/webhook:', code2)

# 8. Check ports
print('\n=== 8. Ports listening ===')
run('ss -tlnp | grep -E "443|:80"')

# 9. Service status
print('\n=== 9. Service status ===')
run('systemctl is-active onmedicina')
run('systemctl is-active nginx')

ssh.close()
print('\nDONE')
