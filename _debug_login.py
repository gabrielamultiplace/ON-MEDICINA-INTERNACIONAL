#!/usr/bin/env python3
"""Debug login on VPS"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('69.62.91.8', username='root', password='@Omedicina2025', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out.strip())
    if err: print('ERR:', err.strip()[:500])
    return out.strip()

print('=== 1. DB file check ===')
run('ls -la /opt/onmedicina/data.db 2>/dev/null || echo "NO DATABASE FILE"')

print('\n=== 2. Users in DB ===')
run('sqlite3 /opt/onmedicina/data.db "SELECT id, name, email, role FROM users;" 2>/dev/null || echo "NO USERS TABLE"')

print('\n=== 3. Login test ===')
login_result = run("curl -s -X POST http://127.0.0.1:5000/api/login -H 'Content-Type: application/json' -d '{\"email\":\"gabrielamultiplace@gmail.com\",\"password\":\"@On2025@\"}'")

print('\n=== 4. Error log (last 40) ===')
run('tail -n 40 /opt/onmedicina/error.log')

print('\n=== 5. Permissions ===')
run('ls -la /opt/onmedicina/data.db 2>/dev/null; ls -la /opt/onmedicina/data/ | head -10')

ssh.close()
print('\nDONE')
