# ⚡ QUICK START - TOKEN ASAAS

## 🚀 Em 30 segundos

### 1. Ver o token na interface
```
1. http://localhost:5000
2. ⚙️ Configurar Sistema
3. Integrações API
4. 🪝 Webhook Asaas → Token Asaas API
```

### 2. Status do token
```
✅ Status: CONFIGURADO
🔑 Token: onmedicinainte...al2026
🌍 Ambiente: production
```

### 3. Usar em código
```python
from app import ASAAS_API_KEY
headers = {'access_token': ASAAS_API_KEY}
```

---

## 📋 O QUE MUDOU

| Item | Antes | Depois |
|------|-------|--------|
| Token | ❌ Não configurado | ✅ Configurado |
| Local | - | `.env` (seguro) |
| Interface | - | ✅ Seção de Token |
| Status | - | ✅ Exibido na interface |
| Endpoints | 0 | +2 endpoints |

---

## ✅ CHECKLIST RÁPIDO

- [x] Token salvo em `.env`
- [x] app.py carrega token
- [x] index.html mostra status
- [x] 2 endpoints funcionando
- [x] Tudo testado e aprovado

---

## 🎯 PRÓXIMO PASSO

Testar criação de pagamento:
```python
from asaas_integration_v2 import AsaasIntegration

asaas = AsaasIntegration()
payment = asaas.criar_pagamento(
    customer_id="cus_123",
    valor=100.00,
    tipo="PIX"
)
```

---

**Status**: 🟢 **PRONTO PARA USAR**

Seu token Asaas está configurado! 🎉
