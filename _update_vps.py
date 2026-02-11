#!/usr/bin/env python3
"""Update VPS via SSH - git pull + restart"""
import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('69.62.91.8', username='root', password='@Omedicina2025', timeout=15)

def run(cmd, timeout=120):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out.strip())
    if err and 'warning' not in err.lower() and 'already' not in err.lower():
        print('ERR:', err[-300:])
    return out.strip()

print('=== 1. Git pull ===')
run('git config --global --add safe.directory /opt/onmedicina')
run('cd /opt/onmedicina && git pull origin main')

print('\n=== 2. Pip install ===')
run('cd /opt/onmedicina && /opt/onmedicina/venv/bin/pip install -r requirements.txt -q')

print('\n=== 3. Restart servico ===')
run('systemctl restart onmedicina')
time.sleep(3)

print('\n=== 4. Status ===')
print(run('systemctl status onmedicina --no-pager -l | head -15'))

print('\n=== 5. Teste HTTP ===')
code = run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000/")
print('HTTP Status:', code)

ssh.close()
print('\nATUALIZACAO CONCLUIDA!')
