# 🚀 GUIA RÁPIDO - Configuração DNS (5 minutos)

## 📊 Seus Dados

```
Domínio:        app.onmedicinainternacional.com
IP Público:     186.232.133.253
Tipo Registro:  A (IPv4)
Hostname:       app
TTL:            3600
```

---

## ✨ 3 Passos Principais

### Passo 1: Acesse o Registrador (1 min)

**Qual é o seu registrador?**
- [ ] GoDaddy
- [ ] Namecheap
- [ ] Hostinger
- [ ] iG/UOL
- [ ] Outro: _________________

**Link de acesso:**
```
GoDaddy:    www.godaddy.com (Login → Meus Produtos → Domínios)
Namecheap:  www.namecheap.com (Login → Dashboard → Domain List)
Hostinger:  www.hostinger.com (Login → Domínios)
iG:         registro.ig.com.br (Login → Meus Domínios)
```

---

### Passo 2: Adicione o Registro A (2 min)

Procure por **"Adicionar Registro"** ou **"+"** e preencha:

```
Tipo:     A
Host:     app
Valor:    186.232.133.253
TTL:      3600
```

Clique em **Salvar** ou **Create**.

---

### Passo 3: Aguarde Propagação (5 min - 48h)

```powershell
# No PowerShell, depois de 1-2 horas, execute:
nslookup app.onmedicinainternacional.com

# Deve mostrar:
# Address: 186.232.133.253
```

Se ainda não resolve, use **dnschecker.org** para monitorar.

---

## 🔧 Configurações Extras (Opcional)

### Se quiser que `onmedicinainternacional.com` redirecione:

```
Tipo:     CNAME
Host:     @
Valor:    app.onmedicinainternacional.com
TTL:      3600
```

---

## 🧪 Teste Rápido

Depois da propagação:

```powershell
cd "c:\Users\Gabriela Resende\Documents\Plataforma ON"
.\Test-DNS.ps1
```

Se tudo passar, então:
```
http://app.onmedicinainternacional.com:5000
```

Deve funcionar!

---

## Precisa de Mais Detalhes?

- **Guia Completo**: `CONFIGURACAO_DNS.md`
- **Checklist Passo a Passo**: `CHECKLIST_DNS.md`
- **Script de Testes**: `Test-DNS.ps1`

---

**Depois que DNS funcionar**: SSL Certificate → Nginx → Produção Final
