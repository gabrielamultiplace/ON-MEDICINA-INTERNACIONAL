#!/usr/bin/env python3
"""Setup Intellisign env vars and reportlab on VPS"""
import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('69.62.91.8', username='root', password='@Omedicina2025', timeout=15)

def run(cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err and 'warning' not in err.lower(): print('ERR:', err[-300:])
    return out

# 1. Add env vars
print('=== 1. Adding Intellisign env vars ===')
run('echo "" >> /opt/onmedicina/.env')
run('echo "INTELLISIGN_CLIENT_ID=a10e6441-964e-4f32-90e1-32c85b93903b" >> /opt/onmedicina/.env')
run('echo "INTELLISIGN_CLIENT_SECRET=a10e6441-964e-4f32-90e1-32c85b93903b" >> /opt/onmedicina/.env')
time.sleep(1)
print('Env vars:')
run('grep INTELLISIGN /opt/onmedicina/.env')

# 2. Install reportlab
print('\n=== 2. Installing reportlab ===')
run('/opt/onmedicina/venv/bin/pip install reportlab -q')
run('/opt/onmedicina/venv/bin/pip show reportlab | head -2')

# 3. Restart
print('\n=== 3. Restart service ===')
run('systemctl restart onmedicina')
time.sleep(3)

# 4. Verify
print('\n=== 4. Verify ===')
run('systemctl is-active onmedicina')
code = run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000/")
print('HTTP:', code)

ssh.close()
print('\nDone!')
