# 🔄 Configurar Nginx como Proxy Reverso

## ⚠️ Situação Atual

✅ DNS configurado: `app.onmedicinainternacional.com` → `186.232.133.253`
✅ Flask rodando: `localhost:5000`
❌ Problema: Nginx não está configurado (porta 80)

Quando você acessa `app.onmedicinainternacional.com`, o navegador tenta porta **80**, mas Flask está na **5000**.

---

## 📋 Solução: Instalar Nginx

### Opção 1: Download Manual (Recomendado)

**1. Baixe Nginx:**
- Acesse: https://nginx.org/en/download.html
- Clique em **"nginx-x.x.x.zip"** (mainline version, ex: 1.27.1)

**2. Extraia o arquivo:**
```powershell
# Supondo que você baixou em C:\Users\seu-usuario\Downloads\nginx-1.27.1.zip
$arquivo = "C:\Users\Gabriela Resende\Downloads\nginx-*.zip"
Expand-Archive -Path $arquivo -DestinationPath "C:\"
Rename-Item -Path "C:\nginx-1.27.1" -NewName "nginx"
```

**3. Verifique a instalação:**
```powershell
dir C:\nginx
```

Deve existir `C:\nginx\nginx.exe`

---

### Opção 2: Chocolatey (Se instalado)

```powershell
# Execute como Administrador
choco install nginx -y
```

---

## ⚙️ Configurar o Nginx

**1. Crie a pasta de configuração:**
```powershell
mkdir "C:\nginx\conf\sites-available" -Force
```

**2. Copie o arquivo de configuração:**
```powershell
Copy-Item "C:\Users\Gabriela Resende\Documents\Plataforma ON\nginx_default.conf" `
  -Destination "C:\nginx\conf\sites-available\default.conf"
```

**3. Modifique o arquivo `C:\nginx\conf\nginx.conf`:**

Adicione esta linha **antes de `}`** na seção `http`:
```nginx
include sites-available/*.conf;
```

Exemplo:
```nginx
http {
    include mime.types;
    default_type application/octet-stream;
    
    # ... outras linhas ...
    
    include sites-available/*.conf;  # ← ADICIONE ESTA LINHA
}
```

**4. Teste a configuração:**
```powershell
cd C:\nginx
.\nginx.exe -t
```

Deve mostrar: `configuration file [.../nginx.conf] test is successful`

---

## ▶️ Iniciar Nginx

```powershell
# Execute como Administrador

# Parar qualquer Nginx em execução
taskkill /F /IM nginx.exe

# Aguarde um segundo
Start-Sleep -Seconds 1

# Iniciar Nginx
cd C:\nginx
.\nginx.exe

# Verificar se iniciou
Get-Process nginx
```

---

## ✅ Testar o Acesso

### 1. Teste local (localhost)
```powershell
curl http://localhost
```

Deve retornar a página do Flask!

### 2. Teste do domínio
Abra no navegador:
```
http://app.onmedicinainternacional.com
```

---

## 🔄 Comandos Úteis

```powershell
# Parar Nginx
taskkill /F /IM nginx.exe

# Reiniciar (reload da config)
cd C:\nginx
.\nginx.exe -s reload

# Parar gracefully
cd C:\nginx
.\nginx.exe -s quit

# Ver logs de erro
Get-Content "C:\nginx\logs\error.log" -Tail 20

# Ver configuração ativa
cd C:\nginx
.\nginx.exe -T
```

---

## 🆘 Troubleshooting

### Erro: "Address already in use"
Significa que algo já está usando porta 80.

```powershell
# Encontrar o processo
netstat -ano | findstr :80

# Parar o processo (substitua PID)
taskkill /F /PID <PID>
```

### Erro: "proxy_pass"]
Certifique-se de que Flask está rodando:
```powershell
netstat -ano | findstr :5000
```

### Nginx não inicia
Verifique os logs:
```powershell
Get-Content C:\nginx\logs\error.log -Tail 50
```

---

## 💾 Cenário Completo de Teste

**Terminal 1: Flask rodando**
```powershell
cd "C:\Users\Gabriela Resende\Documents\Plataforma ON"
python app.py
# Deve mostrar: Running on http://127.0.0.1:5000
```

**Terminal 2: Nginx rodando**
```powershell
cd C:\nginx
.\nginx.exe
```

**Terminal 3: Teste**
```powershell
# Teste local
curl http://localhost

# Teste domínio (quando DNS propagar)
curl http://app.onmedicinainternacional.com
```

---

## 🚀 Depois de Configurado

Seu fluxo será:
```
Navegador: app.onmedicinainternacional.com:80
    ↓
Nginx (localhost:80)
    ↓
Flask (localhost:5000)
    ✓ Página carregada!
```

---

## 📌 Próximos Passos (SSL/HTTPS)

Depois que tiver certeza que HTTP funciona, você pode configurar HTTPS com:
- **Let's Encrypt** (Certificado gratuito)
- **Certbot** (automação)

Avise quando quiser configurar SSL! 🔐
