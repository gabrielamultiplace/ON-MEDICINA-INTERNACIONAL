# 🌐 Configuração DNS - app.onmedicinainternacional.com

## Informações do Servidor

```
IP PÚBLICO:     186.232.133.253
IP LOCAL:       192.168.1.16
HOSTNAME:       DESKTOP-B7H1V55
DOMÍNIO:        app.onmedicinainternacional.com
APLICAÇÃO:      Flask (porta 5000 - será via nginx na porta 80/443)
```

---

## Passo 1: Identificar o Registrador

Você precisa saber **qual empresa registrou o domínio** `onmedicinainternacional.com`. Comum:

- **GoDaddy** (godaddy.com)
- **Namecheap** (namecheap.com)
- **Hostinger** (hostinger.com)
- **iG** (registro.ig.com.br) - Para domínios .com.br
- **Registro.BR** (registro.br) - Para domínios .br
- **Microsoft Azure** (azure.microsoft.com)
- **AWS Route53** (aws.amazon.com)
- **Google Domains** (domains.google.com)
- **CloudFlare** (cloudflare.com)

**Como descobrir:**
```bash
# PowerShell
whois app.onmedicinainternacional.com
```

---

## Passo 2: Acessar o Painel de Controle do Registrador

### 🔴 Se for GoDaddy:
1. Vá para **www.godaddy.com**
2. Faça login com suas credenciais
3. Clique em **"Meus Produtos"** → **Domínios**
4. Clique no domínio **onmedicinainternacional.com**
5. Clique em **"Gerenciar DNS"**

### 🔴 Se for Namecheap:
1. Vá para **www.namecheap.com**
2. Faça login
3. Clique em **"Dashboard"** → **Domain List**
4. Clique em **"Manage"** próximo ao domínio
5. Vá à aba **"Advanced DNS"**

### 🔴 Se for iG/Registro.BR:
1. Vá para **www.registro.ig.com.br**
2. Acesse painel de desenvolvimento/DNS
3. Procure por configuração de registros

### 🔴 Se for AWS Route53:
1. Acesse **AWS Console**
2. Vá para **Route 53** → **Hosted Zones**
3. Selecione **onmedicinainternacional.com**

### 🔴 Se for CloudFlare:
1. Acesse **www.cloudflare.com**
2. Faça login
3. Selecione o domínio
4. Vá à aba **"DNS"**

---

## Passo 3: Adicionar Registros DNS

**IMPORTANTE:** Se o domínio **já está apontando para nameservers customizados**, você precisa configurar UT do registrador ou do servidor DNS.

### Cenário A: Registrador tem painel DNS (mais comum)

Adicione estes registros:

#### **Registro A (Principal - IPv4)**
```
Tipo:           A
Nome/Subdomain: app
Valor/IP:       186.232.133.253
TTL:            3600 (1 hora)
```

#### **Registro AAAA (Opcional - IPv6)**
Se você tem IPv6:
```
Tipo:           AAAA
Nome:           app
Valor:          [seu IPv6]
TTL:            3600
```

#### **Registro CNAME (Opcional - Apex redirect)**
Para redirecionar o apex do domínio:
```
Tipo:           CNAME
Nome:           @ ou onmedicinainternacional.com
Valor:          app.onmedicinainternacional.com
TTL:            3600
```

#### **Registros SPF/MX (Opcional - Se usar email)**
```
Tipo:           MX
Nome:           @ ou onmedicinainternacional.com
Value/Priority: 10 mail.onmedicinainternacional.com
TTL:            3600
```

#### **Registro TXT (Optional - Verificação)**
```
Tipo:           TXT
Nome:           @
Valor:          v=spf1 include:_spf.google.com ~all
TTL:            3600
```

---

### Cenário B: Já tem nameservers customizados? 

Se você já tem um servidor DNS próprio ou usa um provedor DNS (CloudFlare, Route53, etc.):

**Você precisará editar os registros DNS no seu servidor DNS**, não no registrador.

**Exemplo para BIND/PowerDNS:**
```dns
app.onmedicinainternacional.com.    IN A       186.232.133.253
```

---

## Passo 4: Passo a Passo Visual (Exemplo - GoDaddy)

### Na página de DNS do GoDaddy:

1. **Procure por "Adicionar Registro" ou "+"**
2. **Preencha:**
   - Tipo: **A**
   - Hostname: **app**
   - Valor: **186.232.133.253**
   - TTL: **3600**

3. **Clique em Salvar**

4. **Processo se repete para cada registro**

---

## Passo 5: Verificar Propagação DNS

A propagação leva **15 minutos a 48 horas**. Verifique:

```powershell
# Windows - Verificar resolução DNS
nslookup app.onmedicinainternacional.com

# Resultado esperado:
# Name:    app.onmedicinainternacional.com
# Address: 186.232.133.253
```

```bash
# Linux/Mac
dig app.onmedicinainternacional.com
nslookup app.onmedicinainternacional.com
```

**Ferramentas online:**
- **dnschecker.org** - Verifica DNS em múltiplos servidores
- **mxtoolbox.com** - Análise completa de DNS
- **whatsmydns.net** - Mapa global de propagação

---

## Passo 6: Configuração de Firewall/Router

### ⚠️ IMPORTANTE se estiver em rede privada:

Se seu servidor está atrás de um router (rede doméstica/escritório):

1. **Port Forwarding no Router:**
   - Acesse **192.168.1.1** (padrão) no navegador
   - Faça login do router
   - Configure Port Forwarding:
     ```
     Porta Externa: 80 → IP Interno: 192.168.1.16 : 5000 (ou 80)
     Porta Externa: 443 → IP Interno: 192.168.1.16 : 443 (ou 8000 com nginx)
     ```

2. **Firewall do Windows:**
   ```powershell
   # Abrir portas
   New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
   New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
   ```

---

## Resumo da Configuração

| Campo | Valor |
|-------|-------|
| **Domínio** | app.onmedicinainternacional.com |
| **Tipo de Registro** | A (IPv4) |
| **Hostname** | app |
| **IP (Valor)** | 186.232.133.253 |
| **TTL** | 3600 segundos |
| **Tempo Propagação** | 15 min a 48 horas |

---

## Depois que DNS Estiver Configurado

Pode acessar a aplicação em:

```
http://app.onmedicinainternacional.com:5000   (sem HTTPS, com porta)
https://app.onmedicinainternacional.com        (com nginx + SSL - próxima etapa)
```

---

## Próximas Etapas (após DNS funcionar)

1. **SSL Certificate** - Let's Encrypt (HTTPS)
2. **Nginx** - Reverse proxy (porta 80 → 5000)
3. **Production** - Gunicorn + systemd service

Ver: `DEPLOYMENT_GUIDE.md` para detalhes completos.

---

## Troubleshooting

### DNS não está propagando:
```powershell
# Forçar atualização do cache DNS local
ipconfig /flushdns

# Aguardar 15 min - 48 horas
# Checar em: dnschecker.org
```

### Página não abre mesmo após DNS funcionar:
1. Verificar se Flask está rodando: `http://localhost:5000`
2. Verificar se porta 80/443 está aberta no router
3. Verificar Firewall do Windows
4. Tentar IP público direto: `http://186.232.133.253:5000`

### Erro de certificado SSL depois:
- Usar Let's Encrypt (grátis)
- Ver: `DEPLOYMENT_GUIDE.md` Fase 3

---

## Contato com Suporte do Registrador

Se não conseguir configurar, cada registrador tem suporte:
- **GoDaddy**: chat.godaddy.com
- **Namecheap**: live.namecheap.com  
- **Hostinger**: help.hostinger.com
- **iG**: suporte.ig.com.br

Diga ao suporte: *"Quero adicionar um registro A para o subdomínio 'app' apontando para o IP 186.232.133.253"*

---

**Data**: 6 de fevereiro, 2026  
**Status**: Pronto para configuração  
**Próximo**: Após DNS propagar → SSL Certificate → Nginx
