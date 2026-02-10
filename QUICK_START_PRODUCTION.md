# QUICK START PRODUCTION DEPLOYMENT

## Status
- ✅ **Localhost fixed** - Use `http://127.0.0.1:5000` or `http://localhost:5000`
- ✅ **All medications loaded** - 20 items confirmed
- ✅ **Ready for production**

---

## Two Deployment Options

### 🟢 OPTION 1: Windows Deployment (Simple, Recommended for testing)

**Quick Start:**
```powershell
# Run the deployment setup script
.\Deploy-Production.ps1

# This will:
# - Validate Python environment
# - Install Gunicorn
# - Backup data files
# - Test Flask application
```

**Start Production Server:**
```powershell
# Method A: Using Gunicorn (production-grade)
gunicorn -c gunicorn_config.py wsgi:app

# Method B: Using Flask directly (for testing)
python app.py
```

The server will be available at:
- `http://127.0.0.1:5000` (local only)
- `http://192.168.1.16:5000` (local network)
- Cannot be accessed from internet without additional setup

---

### 🔵 OPTION 2: Linux Deployment (Recommended for production)

For production on `app.onmedicinainternacional.com`, deploy to Linux (Ubuntu/Debian):

**Preparation:**
1. Rent a Linux VPS (Linode, DigitalOcean, AWS, etc.)
2. Transfer files to server
3. Follow DEPLOYMENT_GUIDE.md for full setup

**Quick Commands:**
```bash
# SSH to server
ssh user@server-ip

# Navigate to project
cd /home/www-data/plataforma-on

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Test application
python -c "from app import app; print('OK')"

# Start Gunicorn
gunicorn -c gunicorn_config.py wsgi:app &

# Server will listen on 127.0.0.1:8000 (nginx will handle public traffic)
```

---

## DNS Setup (Both Options)

### At Your Domain Registrar (app.onmedicinainternacional.com)

**Go to Domain Registrar Dashboard:**
1. Find "DNS Records" or "Nameservers"
2. Add A Record:
   ```
   Name/Subdomain: app
   Type: A
   Value: YOUR_SERVER_IP
   TTL: 3600
   ```

3. If you have IPv6, add AAAA record:
   ```
   Name: app
   Type: AAAA
   Value: YOUR_IPV6
   TTL: 3600
   ```

**Verify DNS Resolution:**
```powershell
# Windows
nslookup app.onmedicinainternacional.com

# Linux/Mac
dig app.onmedicinainternacional.com
```

Wait 15 minutes to 48 hours for DNS to propagate.

---

## SSL Certificate Setup

### For Windows + IIS:
1. In IIS, right-click site → Edit Bindings
2. Add HTTPS binding
3. Install certificate (use IIS Certificate Wizard)
4. Can use Let's Encrypt Certbot for Windows

### For Linux + Nginx:
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d app.onmedicinainternacional.com

# Certificate will be at:
# /etc/letsencrypt/live/app.onmedicinainternacional.com/

# Auto-renewal
sudo certbot renew --dry-run
sudo systemctl enable certbot.timer
```

---

## Testing Production Setup

### Test Local Application:
```powershell
# Windows
Invoke-WebRequest -Uri "http://localhost:5000/" -UseBasicParsing | Select-Object StatusCode

# Linux
curl -I http://localhost:8000/
```

### Test Production Domain (after DNS + SSL):
```bash
# Check DNS resolution
nslookup app.onmedicinainternacional.com

# Test HTTP (should redirect to HTTPS)
curl -I http://app.onmedicinainternacional.com/

# Test HTTPS
curl -I https://app.onmedicinainternacional.com/

# Check certificate
openssl s_client -connect app.onmedicinainternacional.com:443
```

---

## Monitoring & Maintenance

### Check Server Status:
```bash
# Linux - Check Gunicorn
systemctl status plataforma-on

# Windows - Check if process running
Get-Process | findstr python

# Test health endpoint
curl https://app.onmedicinainternacional.com/health
```

### View Logs:
```bash
# Linux - Application logs
journalctl -u plataforma-on -f

# Linux - Nginx logs
tail -f /var/log/nginx/app.onmedicinainternacional.com_access.log

# Windows - Flask logs (if running in console)
# Visible in terminal where python app.py is running
```

### Backup Data:
```bash
# Windows
Copy-Item -Path "data\*" -Destination "backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Recurse

# Linux
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz data/
```

---

## File Structure After Deployment

```
plataforma-on/
├── app.py                    # Main Flask application
├── wsgi.py                   # WSGI entry point
├── gunicorn_config.py        # Gunicorn production config
├── requirements.txt          # Python dependencies
├── data/
│   ├── medicamentos.json     # Medicine database
│   ├── leads.json           # Leads database
│   └── doctors.json         # Doctors database
├── uploads/                  # User uploads
├── static/                   # CSS, JavaScript
├── templates/               # HTML templates
├── DEPLOYMENT_GUIDE.md      # Detailed deployment guide
├── Deploy-Production.ps1    # PowerShell deployment script
├── DEPLOY_SETUP.bat         # Windows batch setup script
├── nginx.conf.template      # Nginx configuration
└── logs/                    # Application logs
```

---

## Troubleshooting

### Port Already in Use:
```powershell
# Windows
Get-Process | Where-Object {$_.Name -eq "python"} | Stop-Process -Force

# Check what's on port 5000
netstat -ano | findstr :5000

# Linux
lsof -i :8000
kill -9 <PID>
```

### Module Import Errors:
```bash
pip install -r requirements.txt
pip install --upgrade flask

# Check Python path
python -c "import sys; print(sys.path)"
```

### Cannot Access Domain:
1. Check DNS resolution: `nslookup app.onmedicinainternacional.com`
2. Check firewall: Port 80 and 443 open?
3. Check server: Is Flask/Gunicorn running?
4. Check logs: What errors in nginx/gunicorn logs?

### Database Locked:
```bash
# Remove lock file
rm -f data.db-journal

# Restart application
systemctl restart plataforma-on
```

---

## Next Actions

**Immediate** (Today)
1. ✅ Test localhost access: `http://localhost:5000`
2. ✅ Verify all 20 medications load
3. ✅ Backup current data

**This Week**
1. Register/unlock domain `app.onmedicinainternacional.com`
2. Configure DNS A records at registrar
3. Set up SSL certificate (Let's Encrypt)
4. Choose deployment environment:
   - Option A: Keep on local Windows (for testing)
   - Option B: Migrate to Linux VPS (for production)

**Production Deployment**
1. Copy deployment scripts and configs to server
2. Follow DEPLOYMENT_GUIDE.md for complete setup
3. Test all features
4. Set up monitoring and backups

---

## Important Notes

⚠️ **Localhost Access:**
- Only works on same machine or local network
- Not accessible from internet
- Use for development/testing

⚠️ **Production Domain:**
- Requires DNS configuration
- Requires SSL certificate
- Requires internet-accessible server
- Follow DEPLOYMENT_GUIDE.md completely

⚠️ **Data Safety:**
- Always backup `data/` folder before deployment
- Keep backups in multiple locations
- Test restore procedures regularly

⚠️ **Security:**
- Never commit `.env` or secrets to version control
- Keep dependencies updated: `pip install --upgrade -r requirements.txt`
- Monitor logs for errors
- Use strong passwords for admin accounts

---

## Support

For detailed configuration:
- See **DEPLOYMENT_GUIDE.md** (comprehensive guide)
- Run **Deploy-Production.ps1** (PowerShell setup)
- Run **DEPLOY_SETUP.bat** (Windows batch setup)

For each environment:
- **Windows**: DEPLOYMENT_GUIDE.md - Phase 5 Option B (IIS)
- **Linux**: DEPLOYMENT_GUIDE.md - Phase 5 Option A (Nginx + Gunicorn)

---

**Last Updated**: February 6, 2026  
**Status**: Ready for Production Deployment
