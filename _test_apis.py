#!/usr/bin/env python3
"""Test prescription-related APIs on VPS"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('69.62.91.8', username='root', password='@Omedicina2025', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out.strip())
    if err and 'WARNING' not in err.upper(): print('ERR:', err.strip()[:300])
    return out.strip()

print('=== 1. Login test ===')
run("""curl -s -X POST http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"gabrielamultiplace@gmail.com","password":"@On2025@"}'""")

print('\n=== 2. API medicamentos ===')
run("curl -s http://127.0.0.1:5000/api/medicamentos | head -c 1000")

print('\n=== 3. Medicamentos data file ===')
run("cat /opt/onmedicina/data/medicamentos.json | head -c 1000")

print('\n=== 4. Check data files exist ===')
run("ls -la /opt/onmedicina/data/")

print('\n=== 5. Service status ===')
run("systemctl is-active onmedicina")

print('\n=== 6. External access test ===')
run("curl -s -o /dev/null -w '%{http_code}' http://69.62.91.8/api/medicamentos")

ssh.close()
print('\nDONE')
