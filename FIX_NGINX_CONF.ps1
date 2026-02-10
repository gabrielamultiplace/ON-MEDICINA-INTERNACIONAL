$conf = @"
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;

    server {
        listen 80;
        server_name app.onmedicinainternacional.com;
        
        location / {
            proxy_pass http://localhost:5000;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        }
    }
}
"@

[System.IO.File]::WriteAllText("C:\nginx\conf\nginx.conf", $conf, (New-Object System.Text.UTF8Encoding $false))
Write-Host "OK: nginx.conf criado corretamente"

Write-Host "Testando configuracao..."
cd C:\nginx
.\nginx.exe -t
