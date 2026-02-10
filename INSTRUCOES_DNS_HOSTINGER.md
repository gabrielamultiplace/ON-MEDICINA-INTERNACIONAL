# 🌐 Configurar DNS no Hostinger para app.onmedicinainternacional.com

## 📋 Informações do Servidor
- **Domínio:** onmedicinainternacional.com
- **Subdomínio:** app
- **IP do Servidor:** 186.232.133.253

---

## ✅ Passo a Passo - Hostinger

### 1️⃣ Acesse o Painel do Hostinger
- Vá para: https://www.hostinger.com.br/
- Clique em **"Painel de Controle"** ou faça login
- Selecione o domínio **onmedicinainternacional.com**

### 2️⃣ Acesse as Configurações de DNS
- No painel, procure por **"Domínios"** ou **"Gerenciar Domínio"**
- Clique sobre o domínio **onmedicinainternacional.com**
- Vá para a aba **"Registros DNS"** ou **"DNS Zone"**

### 3️⃣ Adicione um Novo Registro A
Clique em **"Adicionar Registro"** ou **"+ Novo Registro"**

Preencha com:
```
Tipo:     A
Nome:     app
Prioridade: (deixe em branco)
Valor:    186.232.133.253
TTL:      3600
```

### 4️⃣ Salve as Alterações
- Clique em **"Salvar"** ou **"Confirmar"**
- Você deve ver uma mensagem: "Registro adicionado com sucesso"

---

## ⏳ Aguarde a Propagação DNS
O registro pode levar entre **15 minutos a 24 horas** para ser propagado em todos os servidores DNS.

### Teste Imediatamente (opcional):
```powershell
# Teste direto no Google DNS
nslookup app.onmedicinainternacional.com 8.8.8.8

# Teste local
nslookup app.onmedicinainternacional.com
```

**Resultado esperado:**
```
Name:    app.onmedicinainternacional.com
Address: 186.232.133.253
```

---

## 🔍 Verificação de DNS

### Teste online:
- https://dnschecker.org/
- https://mxtoolbox.com/
- https://toolbox.googleapps.com/apps/checkmx/

Basta digitar: `app.onmedicinainternacional.com`

---

## 🆘 Se não funcionar após 24h:

### Verifique:
1. ✅ O registro foi salvo no Hostinger?
2. ✅ O domínio está ativo no Hostinger?
3. ✅ Os nameservers estão corretos?
   - Vá em "Configurações do Domínio"
   - Procure por "Nameservers" ou "Servidores de Nomes"
   - Devem ser os do Hostinger (não alterados para outro provedor)

### Nameservers do Hostinger (padrão):
```
ns1.hostinger.com.br
ns2.hostinger.com.br
ns3.hostinger.com.br
```

---

## ✨ Depois de Configurado

Ao acessar **app.onmedicinainternacional.com**, você será redirecionado para:
```
http://186.232.133.253:5000
```

Que é seu servidor Flask local!

---

## 📞 Suporte Hostinger

Se tiver dúvidas, contate o suporte do Hostinger:
- **Chat Live:** https://www.hostinger.com.br/suporte
- **E-mail:** support@hostinger.com.br
- **Telefone:** +55 11 3500-7000

Mencione que quer adicionar um registro A para um subdomínio apontando para um servidor externo.
