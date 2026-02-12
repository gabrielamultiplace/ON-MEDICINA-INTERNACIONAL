#!/usr/bin/env python3
"""Diagnose webhook timeout issue on VPS"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('69.62.91.8', username='root', password='@Omedicina2025', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err: print('ERR:', err[-500:])
    return out

print('=== 1. Service status ===')
run('systemctl is-active onmedicina')

print('\n=== 2. Nginx status ===')
run('systemctl is-active nginx')

print('\n=== 3. Nginx config ===')
run('cat /etc/nginx/sites-enabled/onmedicina 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null || ls /etc/nginx/sites-enabled/')

print('\n=== 4. SSL cert check ===')
run('ls -la /etc/letsencrypt/live/ 2>/dev/null || echo NO_LETSENCRYPT')
run('ls -la /etc/nginx/ssl/ 2>/dev/null || echo NO_NGINX_SSL')

print('\n=== 5. Port 443 listening ===')
run('ss -tlnp | grep 443')

print('\n=== 5b. Port 80 listening ===')
run('ss -tlnp | grep 80')

print('\n=== 6. Test local webhook endpoint ===')
code = run("curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:5000/comercial/webhooks -H 'Content-Type: application/json' -d '{\"event\":\"test\"}'")
print('HTTP:', code)

print('\n=== 7. Nginx error log (last 15) ===')
run('tail -15 /var/log/nginx/error.log 2>/dev/null')

print('\n=== 8. Firewall ===')
run('ufw status 2>/dev/null || echo NO_UFW')

print('\n=== 9. All nginx configs ===')
run('ls -la /etc/nginx/sites-enabled/')

print('\n=== 10. DNS check ===')
run("dig +short app.onmedicinainternacional.com 2>/dev/null || nslookup app.onmedicinainternacional.com 2>/dev/null | tail -3")

print('\n=== 11. Test HTTPS externally ===')
run("curl -sk -o /dev/null -w '%{http_code}' https://app.onmedicinainternacional.com/ --connect-timeout 5 2>/dev/null || echo CURL_FAILED")

ssh.close()
print('\nDONE')
