# DEPLOYMENT GUIDE - app.onmedicinainternacional.com

## Phase 1: Local Validation (✅ COMPLETE)
- [x] Flask server running on localhost:5000
- [x] All medications loaded correctly (20 items)
- [x] Cannabis module initialized
- [x] Asaas integration active
- [x] localhost DNS resolved

## Phase 2: DNS Configuration

### Step 1: Update DNS A Record
**To do at your domain registrar:**
1. Go to domain registrar (where you registered onmedicinainternacional.com)
2. Find DNS settings / Nameservers
3. Create/Update A record:
   - **Hostname**: app
   - **Type**: A (IPv4 address)
   - **Value**: [YOUR_SERVER_IP] (e.g., 192.168.1.16 if local, or your public IP if cloud)
   - **TTL**: 3600 (1 hour)

4. Create AAAA record for IPv6 (if applicable):
   - **Hostname**: app
   - **Type**: AAAA
   - **Value**: [YOUR_IPV6_ADDRESS]

5. Optional - Create apex redirect:
   - **Hostname**: @ or onmedicinainternacional.com
   - **Type**: CNAME
   - **Value**: app.onmedicinainternacional.com

**DNS Propagation Time**: 15 minutes to 48 hours
**Verify DNS**: `nslookup app.onmedicinainternacional.com` or `ping app.onmedicinainternacional.com`

---

## Phase 3: SSL Certificate Setup

### Option A: Let's Encrypt (FREE - Recommended)

**On Windows Server:**
```powershell
# Option 1: Using Certbot with IIS
# Install Certbot: https://certbot.eff.org/instructions?os=windows
# Then run:
certbot certonly --standalone -d app.onmedicinainternacional.com
# Certificate location: C:\Certbot\live\app.onmedicinainternacional.com\

# Option 2: Using Posh-ACME PowerShell module
Install-Module -Name Posh-ACME
$params = @{
    Domain = 'app.onmedicinainternacional.com'
    CertPath = 'C:\Certificates\'
    Email = 'your-email@example.com'
}
# Request certificate
```

**On Linux:**
```bash
sudo apt-get install certbot
sudo certbot certonly --standalone -d app.onmedicinainternacional.com
# Certificate will be in /etc/letsencrypt/live/app.onmedicinainternacional.com/
```

### Option B: Commercial Certificate
- Purchase from GoDaddy, Namecheap, Comodo, etc.
- Follow provider's installation instructions

---

## Phase 4: Application Configuration

### Update app.py for Production:
```python
# In app.py, modify the run configuration:
if __name__ == '__main__':
    # Development
    # app.run(debug=True, port=5000)
    
    # Production
    app.run(
        host='0.0.0.0',
        port=8000,  # Gunicorn will handle this
        debug=False,
        threaded=True
    )
```

### Environment Variables:
Create `.env` file in project root:
```
FLASK_ENV=production
FLASK_DEBUG=0
SQLALCHEMY_ECHO=False
ASAAS_TOKEN=your_asaas_token
ASAAS_ENVIRONMENT=production
```

---

## Phase 5: Web Server Setup

### Option A: Nginx + Gunicorn (Linux)

**Install Gunicorn:**
```bash
pip install gunicorn
```

**Nginx Configuration** (`/etc/nginx/sites-available/app.onmedicinainternacional.com`):
```nginx
upstream plataforma_on {
    server 127.0.0.1:8000;  # Gunicorn port
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name app.onmedicinainternacional.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name app.onmedicinainternacional.com;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/app.onmedicinainternacional.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.onmedicinainternacional.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/app.onmedicinainternacional.com_access.log;
    error_log /var/log/nginx/app.onmedicinainternacional.com_error.log;

    # Client upload size
    client_max_body_size 100M;

    location / {
        proxy_pass http://plataforma_on;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "upgrade";
        proxy_set_header Upgrade $http_upgrade;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Static files (if using)
    location /static/ {
        alias /home/username/plataforma-on/static/;
        expires 30d;
    }
}
```

**Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/app.onmedicinainternacional.com /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

**Start Gunicorn:**
```bash
cd /home/username/plataforma-on
gunicorn -c gunicorn_config.py wsgi:app
# Or use systemd service (see below)
```

**Create Systemd Service** (`/etc/systemd/system/plataforma-on.service`):
```ini
[Unit]
Description=Plataforma ON Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/username/plataforma-on
ExecStart=/usr/bin/gunicorn -c gunicorn_config.py wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable plataforma-on
sudo systemctl start plataforma-on
sudo systemctl status plataforma-on
```

---

### Option B: IIS + Haystack (Windows)

**Install FastCGI:**
1. In Server Manager: Add Role Services → Web Server → CGI
2. Install FastCGI module for Python

**Configure IIS:**
1. Create new site in IIS
2. Add binding: `https://app.onmedicinainternacional.com`
3. Point to project folder
4. Configure FastCGI for Python
5. Upload SSL certificate

---

## Phase 6: Firewall & Security

### Windows Firewall (if hosting on Windows):
```powershell
# Allow ports 80 and 443
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow

# Block port 8000 (Gunicorn internal)
New-NetFirewallRule -DisplayName "Block Gunicorn" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Block
```

### Linux (UFW):
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Only localhost should access Gunicorn
```

---

## Phase 7: Verification & Monitoring

### Test Domain Access:
```bash
# Test HTTP (should redirect to HTTPS)
curl -I http://app.onmedicinainternacional.com

# Test HTTPS
curl -I https://app.onmedicinainternacional.com

# Test with certificate validation
openssl s_client -connect app.onmedicinainternacional.com:443
```

### Monitor Logs:
```bash
# Nginx
tail -f /var/log/nginx/app.onmedicinainternacional.com_access.log
tail -f /var/log/nginx/app.onmedicinainternacional.com_error.log

# Gunicorn
journalctl -u plataforma-on -f
```

### Health Check Endpoint (Optional - Add to app.py):
```python
@app.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}, 200
```

Test: `curl https://app.onmedicinainternacional.com/health`

---

## Phase 8: SSL Certificate Auto-Renewal

### Let's Encrypt Auto-Renewal (Linux):
```bash
# Install renewal timer
sudo apt-get install certbot-nginx
sudo certbot renew --dry-run  # Test renewal process
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Manual Renewal:
```bash
sudo certbot renew --force-renewal

# Then reload Nginx
sudo systemctl reload nginx
```

---

## Production Checklist

- [ ] DNS A record pointing to server IP
- [ ] SSL certificate installed and valid
- [ ] Nginx/IIS reverse proxy configured
- [ ] Gunicorn/WSGI server running
- [ ] Firewall rules allowing 80/443, blocking 8000
- [ ] HTTPS redirect working
- [ ] Static files served correctly
- [ ] Database backed up
- [ ] Error logging configured
- [ ] Performance monitoring enabled
- [ ] Uptime monitoring configured
- [ ] Email alerts configured

---

## IMMEDIATE NEXT STEPS

**For Windows Environment:**
1. ✅ Localhost working on 127.0.0.1:5000
2. ⏳ If staying on Windows:
   - Use IIS with FastCGI (simpler on Windows)
   - Or use nssm to run Gunicorn as Windows service
3. ⏳ Register SSL certificate in Windows Certificate Store
4. ⏳ Update DNS at registrar

**For Linux Environment:**
1. Follow Nginx + Gunicorn path above
2. Uses Certbot for Let's Encrypt auto-renewal
3. Native systemd integration

---

## Quick Command Reference

```bash
# Test Flask locally
python app.py

# Run Gunicorn
gunicorn -c gunicorn_config.py wsgi:app

# Check if port is free
netstat -tulpn | grep :8000

# Check DNS
nslookup app.onmedicinainternacional.com

# Test SSL certificate
openssl s_client -connect app.onmedicinainternacional.com:443 </dev/null

# View certificate details
openssl x509 -in /etc/letsencrypt/live/app.onmedicinainternacional.com/cert.pem -text -noout
```

---

**Created**: February 6, 2026  
**Domain**: app.onmedicinainternacional.com  
**Status**: Ready for deployment
