# ✅ CHECKLIST - Configuração DNS para app.onmedicinainternacional.com

## Informações Gerais
- **Domínio Principal**: onmedicinainternacional.com
- **Subdomínio**: app.onmedicinainternacional.com
- **IP Público**: 186.232.133.253
- **IP Local**: 192.168.1.16
- **Porta Aplicação**: 5000
- **Status**: Pronto para configuração

---

## 📋 PASSO 1: Descobrir o Registrador

### ☐ Etapa 1.1: Verificar Registrador
```powershell
# Abrir PowerShell e executar:
whois app.onmedicinainternacional.com
# ou acesso: https://www.whois.com

# Procure por "Registrar" ou "Registrant Organization"
```

**Registrador identificado**: _________________ (anotar aqui)

### ☐ Etapa 1.2: Anote Credenciais
- **Email de Login**: _________________
- **Senha**: __________ (guardar com segurança)
- **URL de Acesso**: _________________

---

## 🌐 PASSO 2: Acessar o Painel de DNS

### ☐ Etapa 2.1: Login no Painel

**Procedimento por Registrador:**

#### Se for **GoDaddy**:
- [ ] Ir para www.godaddy.com
- [ ] Login com email/senha
- [ ] "Meus Produtos" → "Domínios"
- [ ] Clicar em onmedicinainternacional.com
- [ ] Botão "Gerenciar DNS"
- [ ] Procurar "Adicionar Registro" ou "+"

#### Se for **Namecheap**:
- [ ] Ir para www.namecheap.com
- [ ] Login
- [ ] "Dashboard" → "Domain List"
- [ ] Clique "Manage" no domínio
- [ ] Aba "Advanced DNS"
- [ ] Procurar "Add New Record"

#### Se for **Hostinger**:
- [ ] Ir para www.hostinger.com
- [ ] Login
- [ ] "Domínios"
- [ ] Clicar no domínio
- [ ] "Gerenciar DNS"
- [ ] "Adicionar Nova Entrada"

#### Se for **iG/UOL**:
- [ ] Ir para registro.ig.com.br
- [ ] Login
- [ ] Menu "Meus Domínios"
- [ ] Clicar em onmedicinainternacional.com
- [ ] Opção "Configurar DNS"

---

## 📝 PASSO 3: Adicionar Registros DNS

### ☐ Etapa 3.1: Adicionar Registro A (PRINCIPAL)

**Campos a preencher:**

| Campo | Valor |
|-------|-------|
| **Tipo** | A |
| **Nome/Host** | app |
| **Valor/IP** | 186.232.133.253 |
| **TTL** | 3600 |

**Instruções:**
1. [ ] Clique em "Adicionar Registro" ou "+"
2. [ ] Selecione Tipo: **A**
3. [ ] Nome: **app**
4. [ ] Valor: **186.232.133.253**
5. [ ] TTL: **3600**
6. [ ] Clique em **Salvar** ou **Create**

---

### ☐ Etapa 3.2: (Opcional) Adicionar Registro CNAME para Apex

**Se quiser que `onmedicinainternacional.com` redirecione para `app.onmedicinainternacional.com`:**

| Campo | Valor |
|-------|-------|
| **Tipo** | CNAME |
| **Nome/Host** | @ ou onmedicinainternacional.com |
| **Valor** | app.onmedicinainternacional.com |
| **TTL** | 3600 |

**Instruções:**
1. [ ] Clique em "Adicionar Registro"
2. [ ] Tipo: **CNAME**
3. [ ] Nome: **@**
4. [ ] Valor: **app.onmedicinainternacional.com**
5. [ ] TTL: **3600**
6. [ ] Salvar

---

### ☐ Etapa 3.3: (Opcional) Adicionar IPv6 (AAAA)

Se seu servidor suporta IPv6:

| Campo | Valor |
|-------|-------|
| **Tipo** | AAAA |
| **Nome/Host** | app |
| **Valor** | [seu IPv6] |
| **TTL** | 3600 |

---

## ⏳ PASSO 4: Aguardar Propagação

### ☐ Etapa 4.1: Tempo de Espera
- **Tempo esperado**: 15 minutos a 48 horas
- **Data/Hora iniciada**: _______________
- **Data/Hora esperada de propagação**: _______________

### ☐ Etapa 4.2: Ferramenta Online para Verificar

**Use uma destas ferramentas para monitorar:**

1. **dnschecker.org**
   - [ ] Acesse https://dnschecker.org
   - [ ] Digite: **app.onmedicinainternacional.com**
   - [ ] Procure pelo IP: **186.232.133.253**
   - [ ] Quando todos os servidores mostrarem este IP, está propagado

2. **mxtoolbox.com**
   - [ ] Acesse https://mxtoolbox.com/dnsresult.aspx
   - [ ] Digite: **app.onmedicinainternacional.com**
   - [ ] Deve mostrar: **A Record: 186.232.133.253**

---

## 🧪 PASSO 5: Verificar Resolução Local

### ☐ Etapa 5.1: Teste no PowerShell

Quando a propagação terminar:

```powershell
# Abrir PowerShell e executar:
nslookup app.onmedicinainternacional.com

# Resultado esperado:
# Server:  8.8.8.8
# Address: 8.8.8.8
# 
# Name:    app.onmedicinainternacional.com
# Address: 186.232.133.253
```

- [ ] Teste realizado em: _______________
- [ ] Resultado obtido: _______________

### ☐ Etapa 5.2: Limpar Cache Local

Se ainda não resolver (erro de cache):

```powershell
ipconfig /flushdns
ipconfig /registerdns
```

Aguarde 10 segundos e teste novamente.

---

## 🔧 PASSO 6: Configuração de Firewall/Router

### ☐ Etapa 6.1: Port Forwarding no Router

Se seu servidor está atrás de um router (rede doméstica):

1. [ ] Acesse **192.168.1.1** no navegador
2. [ ] Login (padrão: admin/admin)
3. [ ] Procure "Port Forwarding" ou "Encaminhamento de Porta"
4. [ ] Configure:
   - Porta Externa: **80**
   - IP Interno: **192.168.1.16**
   - Porta Interna: **80** (se via nginx) ou **5000** (se direto)

5. [ ] Configure:
   - Porta Externa: **443**
   - IP Interno: **192.168.1.16**
   - Porta Interna: **443** (https via nginx)

6. [ ] Salve as configurações

---

### ☐ Etapa 6.2: Abrir Portas no Firewall do Windows

```powershell
# Abrir PowerShell como ADMINISTRADOR e executar:

# Permitir porta 80 (HTTP)
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow

# Permitir porta 443 (HTTPS)
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow

# Permitir porta 5000 (Flask - opcional, se direto)
New-NetFirewallRule -DisplayName "Flask-App" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

---

## 🚀 PASSO 7: Verificar Conectividade

### ☐ Etapa 7.1: Executar Script de Teste

```powershell
# No PowerShell, execute:
cd "c:\Users\Gabriela Resende\Documents\Plataforma ON"
.\Test-DNS.ps1
```

Espere pelos resultados e verifique:
- [ ] DNS Resolvido
- [ ] Ping Sucesso
- [ ] HTTP Respondendo
- [ ] Python Rodando

---

### ☐ Etapa 7.2: Teste Manual

```powershell
# Testar acesso ao domínio
Invoke-WebRequest -Uri "http://app.onmedicinainternacional.com:5000/" -UseBasicParsing | Select-Object StatusCode

# Resultado esperado: StatusCode: 200
```

---

## 📊 PASSO 8: Verificação Final

### ☐ Etapa 8.1: Acessar via Navegador

- [ ] Acesso via localhost: `http://localhost:5000` ✅
- [ ] Acesso via IP local: `http://192.168.1.16:5000` ✅
- [ ] Acesso via domínio: `http://app.onmedicinainternacional.com:5000` ✅

### ☐ Etapa 8.2: Verificar Medicamentos

- [ ] Página carrega corretamente
- [ ] Medicamentos aparecem (20 items)
- [ ] Sem erros no console (F12)

---

## 🎯 PRÓXIMAS ETAPAS

Depois que **DNS estiver funcionando**:

### [ ] 1. Instalar SSL Certificate
- Veja: `DEPLOYMENT_GUIDE.md` (Fase 3)
- Usar Let's Encrypt (grátis)
- Para Windows: Certbot
- Para Linux: Certbot + Nginx

### [ ] 2. Remover Porta da URL
- Configurar Nginx para redirecionar 80 → 5000
- Acessar sem `:5000` na URL

### [ ] 3. Produção Final
- Instalar Gunicorn
- Configurar como serviço do Windows ou systemd (Linux)
- Monitoramento contínuo

---

## 📞 Suporte

Se tiver dúvidas em cada etapa:

**GoDaddy**: https://www.godaddy.com/help  
**Namecheap**: https://namecheap.com/support/  
**Hostinger**: https://support.hostinger.com/  
**iG**: https://resposta.ig.com.br/

---

## ✅ Conclusão

Uma vez completado este checklist:

- ✅ Domínio configurado
- ✅ DNS propagado
- ✅ Serviço acessível
- ✅ Pronto para SSL + Nginx + Produção

---

**Data de Início**: 6 de fevereiro, 2026  
**Status**: _____________  
**Data de Conclusão**: _____________  

**Assinado**: ________________________
