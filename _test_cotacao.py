import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('69.62.91.8', username='root', password='@Omedicina2025')
stdin, stdout, stderr = ssh.exec_command('curl -s https://economia.awesomeapi.com.br/last/USD-BRL')
print('Response:', stdout.read().decode())
print('Error:', stderr.read().decode())
ssh.close()
