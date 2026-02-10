# 🔗 INTEGRAÇÃO ASAAS - DOCUMENTAÇÃO COMPLETA

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Configuração](#configuração)
3. [Arquitetura](#arquitetura)
4. [Uso da API](#uso-da-api)
5. [Métodos de Pagamento](#métodos-de-pagamento)
6. [Webhooks](#webhooks)
7. [Tratamento de Erros](#tratamento-de-erros)
8. [Testes](#testes)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

A integração com Asaas permite que a plataforma ON Medicina processe pagamentos através de:
- **PIX**: Transferência instantânea com QR Code
- **Boleto**: Pagamento tradicional com código de barras
- **Cartão de Crédito**: Pagamento seguro via redirecionamento

### Endpoints Disponíveis

```
POST   /api/asaas/criar-pagamento              → Criar pagamento com 3 opções
GET    /api/asaas/obter-cobranca/<id>          → Obter status da cobrança
POST   /api/asaas/confirmar-pagamento          → Confirmar pagamento
POST   /api/asaas/webhook                      → Receber eventos de pagamento
GET    /api/asaas/status-pagamento/<lead_id>   → Status por lead
GET    /api/asaas/teste                        → Testar conexão
```

---

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Asaas API
ASAAS_API_KEY=$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmNiOGQ2OWQ0LTRkNGMtNDhiYi04M2Q4LTJiZTRmNDk0MDgxMDo6JGFhY2hfYTVhY2NmY2QtNzBlMS00N2FlLWI2YjYtYjFiMzFlN2UyNTNh
ASAAS_SANDBOX=false                            # Use 'true' para testes
ASAAS_WEBHOOK_URL=https://app.onmedicinainternacional.com/comercial/webhook-setup
ASAAS_WEBHOOK_SECRET=seu_webhook_secret_aqui
```

### 2. Arquivos Necessários

```
Plataforma ON/
├── app.py                        (Flask principal - modificado)
├── index.html                    (Frontend - modificado)
├── asaas_integration_v2.py       (Novo - Módulo Asaas)
├── asaas_config.py              (Novo - Configuração centralizada)
└── ASAAS_INTEGRATION.md         (Este arquivo)
```

### 3. Importações no app.py

```python
# Importação automática (com fallback)
try:
    from asaas_integration_v2 import AsaasIntegration, criar_pagamento_completo
except ImportError:
    AsaasIntegration = None
    criar_pagamento_completo = None
```

---

## 🏗️ Arquitetura

### Camadas de Integração

```
┌─────────────────────────────┐
│   Frontend (index.html)     │
│  - Modal de Pagamento       │
│  - Seleção de Método        │
│  - Status de Pagamento      │
└──────────────┬──────────────┘
               │
               ↓
┌─────────────────────────────┐
│   API Routes (app.py)       │
│  - criar-pagamento          │
│  - obter-cobranca           │
│  - confirmar-pagamento      │
│  - webhook                  │
│  - status-pagamento         │
└──────────────┬──────────────┘
               │
               ↓
┌─────────────────────────────┐
│ AsaasIntegration (V2)       │
│ - criar_cobranca()          │
│ - obter_cobranca()          │
│ - confirmar_pagamento()     │
│ - obter_dados_pix()         │
│ - obter_dados_boleto()      │
└──────────────┬──────────────┘
               │
               ↓
┌─────────────────────────────┐
│  API Asaas (Produção)       │
│  https://api.asaas.com/v3   │
└─────────────────────────────┘
```

### Fluxo de Pagamento

```
1. Usuário clica "Gerar Link de Pagamento"
                 ↓
2. Modal abre com seleção de valor
                 ↓
3. Usuário seleciona método (PIX/Boleto/Cartão)
                 ↓
4. Frontend chama POST /api/asaas/criar-pagamento
                 ↓
5. Backend cria cliente Asaas
                 ↓
6. Backend cria 3 cobrações (uma para cada método)
                 ↓
7. Asaas retorna dados (QR Code, Barcode, URL)
                 ↓
8. Frontend exibe opção selecionada
                 ↓
9. Usuário realiza pagamento
                 ↓
10. Asaas processa pagamento
                 ↓
11. Webhook notifica sistema
                 ↓
12. Sistema atualiza status no banco de dados
                 ↓
13. Lead convertido para Paciente automaticamente
```

---

## 📱 Uso da API

### 1. Criar Pagamento Completo

**Frontend (JavaScript):**

```javascript
async function gerarPagamento(lead, valor) {
    const response = await fetch('/api/asaas/criar-pagamento', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            lead_id: lead.id,
            lead_name: lead.name,
            lead_email: lead.email,
            lead_cpf: lead.cpf,
            amount: valor
        })
    });
    
    return await response.json();
}

// Uso
const resultado = await gerarPagamento(lead, 150.00);
console.log(resultado.payment_options);
// {
//   pix: { qr_code, copy_paste, charge_id, ... },
//   boleto: { barcode, digitable_line, charge_id, ... },
//   credit_card: { payment_url, charge_id, ... }
// }
```

**Backend (Python):**

```python
from asaas_integration_v2 import criar_pagamento_completo

payment = criar_pagamento_completo(
    lead={
        'name': 'João Silva',
        'email': 'joao@example.com',
        'cpf': '12345678901234'
    },
    valor=150.00,
    descricao='Consulta Médica'
)

if payment.get('success'):
    pix = payment['payment_options']['pix']
    print(f"QR Code: {pix['qr_code']}")
    print(f"Copiar/Colar: {pix['copy_paste']}")
```

### 2. Obter Status de Pagamento

**Request:**
```
GET /api/asaas/status-pagamento/lead_123
```

**Response:**
```json
{
    "success": true,
    "lead_id": "lead_123",
    "amount": 150.00,
    "status": "pending",
    "payment_data": {
        "pix": {...},
        "boleto": {...},
        "credit_card": {...}
    },
    "created_at": "2024-01-15T10:30:00Z"
}
```

### 3. Confirmar Pagamento

**Request:**
```json
POST /api/asaas/confirmar-pagamento
{
    "lead_id": "lead_123",
    "charge_id": "chg_123456"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Pagamento confirmado",
    "lead_id": "lead_123",
    "status": "confirmed"
}
```

---

## 💳 Métodos de Pagamento

### PIX

**Características:**
- Transferência instantânea
- QR Code dinâmico
- Código para copiar/colar
- Expiração em 60 minutos (padrão)

**Dados Retornados:**
```json
{
    "pix": {
        "charge_id": "chg_123456",
        "qr_code": "data:image/png;base64,...",
        "copy_paste": "00020126580014br.gov.bcb...",
        "value": 150.00,
        "status": "PENDING",
        "qr_code_url": "https://..."
    }
}
```

**Exibição no Frontend:**

```html
<div style="background: white; padding: 20px; border-radius: 8px;">
    <p>Escaneie com seu banco ou app do PIX:</p>
    <img src="[qr_code]" style="max-width: 300px;">
    
    <p>Ou copie a chave:</p>
    <input readonly value="[copy_paste]" />
    <button onclick="navigator.clipboard.writeText('[copy_paste]')">
        Copiar
    </button>
</div>
```

### Boleto

**Características:**
- Pagamento tradicional
- Código de barras (8 dígitos)
- Linha digitável (47 dígitos)
- PDF para impressão
- Vencimento em 30 dias (padrão)

**Dados Retornados:**
```json
{
    "boleto": {
        "charge_id": "chg_123456",
        "barcode": "12345678901234567890123456",
        "digitable_line": "12345.67890 12345.678901 12345.678901 1 23456789012345",
        "invoice_url": "https://asaas.com/...",
        "value": 150.00,
        "due_date": "2024-02-15",
        "status": "PENDING"
    }
}
```

**Exibição no Frontend:**

```html
<div style="background: white; padding: 20px;">
    <p>Linha Digitável:</p>
    <input readonly value="[digitable_line]" />
    <button onclick="navigator.clipboard.writeText('[digitable_line]')">
        Copiar
    </button>
    
    <a href="[invoice_url]" target="_blank">
        📄 Baixar PDF
    </a>
</div>
```

### Cartão de Crédito

**Características:**
- Pagamento seguro
- Redirecionamento para Asaas
- Processamento em tempo real
- Múltiplas parcelas (configurável)

**Dados Retornados:**
```json
{
    "credit_card": {
        "charge_id": "chg_123456",
        "payment_url": "https://sandbox.asaas.com/checkout/...",
        "value": 150.00,
        "status": "PENDING"
    }
}
```

**Exibição no Frontend:**

```javascript
window.open(payment_url, '_blank', 'width=800,height=600');

// Aguardar confirmação em background
setTimeout(async () => {
    await confirmarPagamento(lead.id, charge_id);
}, 3000);
```

---

## 🔔 Webhooks

### Configuração

1. **Acesse o Asaas:**
   - URL: https://app.asaas.com
   - Seção: Webhooks

2. **Configure a URL:**
   ```
   https://app.onmedicinainternacional.com/comercial/webhook-setup
   ```

3. **Selecione eventos:**
   - ✅ PAYMENT_RECEIVED (Pagamento recebido)
   - ✅ PAYMENT_CONFIRMED (Pagamento confirmado)
   - ✅ PAYMENT_FAILED (Pagamento falhou)
   - ✅ PAYMENT_OVERDUE (Pagamento em atraso)

### Processar Webhook

**Backend (app.py):**

```python
@app.route('/api/asaas/webhook', methods=['POST'])
def webhook_asaas():
    data = request.get_json()
    event = data.get('event')
    
    if event == 'PAYMENT_RECEIVED':
        charge_id = data['charge']['id']
        amount = data['charge']['value']
        
        # Atualizar banco de dados
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            'UPDATE payments SET status = ? WHERE charge_id = ?',
            ('received', charge_id)
        )
        conn.commit()
        conn.close()
        
        # Converter lead para paciente
        moveLeadToPaciente(charge_id)
        
        return jsonify({'success': True})
    
    return jsonify({'success': True})
```

### Eventos Suportados

```
┌────────────────────────────────────────────────────────────────┐
│                      EVENTOS DE PAGAMENTO                     │
├────────────────────────┬────────────────────────────────────────┤
│ Evento                 │ Descrição                             │
├────────────────────────┼────────────────────────────────────────┤
│ PAYMENT_RECEIVED       │ Pagamento foi recebido                │
│ PAYMENT_CONFIRMED      │ Pagamento foi confirmado              │
│ PAYMENT_FAILED         │ Pagamento falhou                      │
│ PAYMENT_OVERDUE        │ Pagamento está em atraso              │
│ INVOICE_CREATED        │ Cobrança foi criada                   │
│ INVOICE_UPDATED        │ Cobrança foi atualizada               │
│ INVOICE_DELETED        │ Cobrança foi deletada                 │
└────────────────────────┴────────────────────────────────────────┘
```

---

## ⚠️ Tratamento de Erros

### Tipos de Erro

#### 1. Erro de Conexão
```python
if result.get('error'):
    message = result.get('message')  # Ex: "Timeout na requisição"
    status = result.get('status_code')
    
    # Fallback: permitir pagamento manual
    return {'success': False, 'fallback': True}
```

#### 2. Erro de Validação
```python
# Email inválido
{
    "error": True,
    "message": "Email must be a valid email",
    "status_code": 400
}

# CPF inválido
{
    "error": True,
    "message": "Invalid CPF",
    "status_code": 400
}
```

#### 3. Erro de Autenticação
```python
# API Key inválida
{
    "error": True,
    "message": "Unauthorized",
    "status_code": 401
}

# Token expirado
{
    "error": True,
    "message": "Token expired",
    "status_code": 401
}
```

### Estratégia de Fallback

```python
def criar_pagamento_com_fallback(lead, valor):
    try:
        return criar_pagamento_completo(lead, valor)
    except Exception as e:
        logger.error(f"Erro Asaas: {str(e)}")
        
        # Modo fallback: pagamento simulado
        return {
            "success": True,
            "fallback": True,
            "payment_options": {
                "demo": {
                    "charge_id": f"demo_{uuid.uuid4()}",
                    "value": valor,
                    "message": "Sistema de pagamento em manutenção. Usando modo demo."
                }
            }
        }
```

---

## 🧪 Testes

### Testar Conexão

```bash
# Python
python3
>>> from asaas_integration_v2 import AsaasIntegration
>>> asaas = AsaasIntegration()
>>> asaas.testar_conexao()
{'success': True}
```

### Testar Endpoint via cURL

```bash
# Teste de conexão
curl http://localhost:5000/api/asaas/teste

# Criar pagamento
curl -X POST http://localhost:5000/api/asaas/criar-pagamento \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "lead_123",
    "lead_name": "João Silva",
    "lead_email": "joao@example.com",
    "lead_cpf": "12345678901234",
    "amount": 150.00
  }'

# Obter status
curl http://localhost:5000/api/asaas/status-pagamento/lead_123
```

### Dados de Teste (Sandbox)

```python
# PIX
valor = 100.00  # Qualquer valor

# Boleto
# Use qualquer CPF válido
# Número do boleto será gerado automaticamente

# Cartão
# Cartão: 4111111111111111
# CVV: 123
# Data: 12/2025
```

---

## 🔧 Troubleshooting

### Problema: "API Key não configurada"

```
❌ Erro: API Key do Asaas não configurada
```

**Solução:**
```python
# Verificar variável de ambiente
import os
api_key = os.getenv('ASAAS_API_KEY')
print(api_key)  # Deve conter a chave

# Ou adicionar ao arquivo .env
ASAAS_API_KEY=$aact_prod_...
```

### Problema: "Email inválido"

```
❌ Erro: Email must be a valid email
```

**Solução:**
```python
# Validar email no lead
import re

email = lead.get('email', 'noreply@onmedicina.com')
if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
    email = 'noreply@onmedicina.com'
```

### Problema: "CPF inválido"

```
❌ Erro: Invalid CPF
```

**Solução:**
```python
# Sanitizar CPF
cpf = ''.join(c for c in lead.get('cpf', '12345678901234') if c.isdigit())[:14]
```

### Problema: "Timeout na requisição"

```
⏱️ Erro: Timeout na requisição
```

**Solução:**
1. Verificar conexão de internet
2. Aumentar timeout (padrão: 10s)
3. Usar modo fallback

### Problema: "Webhook não está recebendo eventos"

**Checklist:**
- [ ] URL do webhook configurada corretamente no Asaas
- [ ] URL está acessível externamente (não é localhost)
- [ ] Método HTTP é POST
- [ ] Headers estão corretos
- [ ] Status da resposta é 200

```python
# Testar webhook manualmente
curl -X POST https://app.onmedicinainternacional.com/comercial/webhook-setup \
  -H "Content-Type: application/json" \
  -d '{
    "event": "PAYMENT_RECEIVED",
    "charge": {
      "id": "chg_test_123",
      "value": 100.00
    }
  }'
```

---

## 📊 Banco de Dados

### Tabela: payments

```sql
CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, confirmed, failed
    payment_data TEXT,               -- JSON com dados de pagamento
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Exemplo de Registro

```json
{
    "id": "pay_123456",
    "lead_id": "lead_123",
    "amount": 150.00,
    "status": "confirmed",
    "payment_data": {
        "customer_id": "cust_123456",
        "payment_options": {
            "pix": {
                "charge_id": "chg_pix_123",
                "qr_code": "data:image/png;base64,...",
                "status": "RECEIVED"
            },
            "boleto": {
                "charge_id": "chg_boleto_123",
                "barcode": "12345678901234567890123456",
                "status": "PENDING"
            },
            "credit_card": {
                "charge_id": "chg_card_123",
                "status": "PENDING"
            }
        }
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
}
```

---

## 📝 Logs

### Exemplo de Log

```
[2024-01-15 10:30:00] INFO: 🔗 AsaasIntegration inicializado
[2024-01-15 10:30:00] INFO:    URL: https://api.asaas.com/v3
[2024-01-15 10:30:00] INFO:    Sandbox: false
[2024-01-15 10:30:01] INFO: 💳 Criando pagamento completo para João Silva - R$ 150.00
[2024-01-15 10:30:01] INFO: 👤 Criando cliente: João Silva
[2024-01-15 10:30:02] INFO: 📤 POST /customers
[2024-01-15 10:30:02] INFO: 📥 Status: 200
[2024-01-15 10:30:02] INFO: 💰 Criando cobrança: PIX de R$ 150.00
[2024-01-15 10:30:02] INFO: 📤 POST /charges
[2024-01-15 10:30:03] INFO: 📥 Status: 200
[2024-01-15 10:30:03] INFO: ✅ Cobrança PIX criada: chg_123456
```

---

## 🔐 Segurança

### Boas Práticas

1. **Nunca exponha a API Key:**
   ```python
   # ❌ Errado
   api_key = "$aact_prod_..."  # Hardcoded
   
   # ✅ Correto
   api_key = os.getenv('ASAAS_API_KEY')
   ```

2. **Valide dados antes de enviar:**
   ```python
   def validar_lead(lead):
       required = ['name', 'email', 'cpf']
       for field in required:
           if not lead.get(field):
               raise ValueError(f"Campo obrigatório: {field}")
   ```

3. **Use HTTPS em produção:**
   ```python
   # Webhooks devem usar HTTPS
   WEBHOOK_URL = "https://app.onmedicinainternacional.com/comercial/webhook-setup"
   ```

4. **Valide assinatura de webhook:**
   ```python
   import hmac
   import hashlib
   
   def validar_webhook(request_data, signature):
       secret = os.getenv('ASAAS_WEBHOOK_SECRET')
       body = json.dumps(request_data)
       expected = hmac.new(
           secret.encode(),
           body.encode(),
           hashlib.sha256
       ).hexdigest()
       return hmac.compare_digest(expected, signature)
   ```

---

## 📚 Referências

- [Documentação Asaas](https://docs.asaas.com/)
- [API Reference](https://docs.asaas.com/reference/overview)
- [Guia de Integração](https://docs.asaas.com/docs/getting-started)
- [Testes Sandbox](https://docs.asaas.com/docs/testing)

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a seção [Troubleshooting](#troubleshooting)
2. Verifique os logs em `/logs/asaas.log`
3. Contate o suporte Asaas: https://suporte.asaas.com

---

**Versão:** 2.0  
**Última atualização:** 2024-01-15  
**Status:** ✅ Produção
