# ⚡ COMO EXECUTAR - ASAAS INTEGRATION

## 🪟 Windows

### Opção 1: Executar o Batch (Recomendado)
```powershell
.\INICIAR_ASAAS.bat
```

### Opção 2: Executar o PowerShell Script (Novo!)
```powershell
.\iniciar.ps1
```

### Opção 3: Manual
```powershell
# Ativar venv
.\venv\Scripts\Activate.ps1

# Iniciar servidor
python app.py
```

---

## 🐧 Linux / Mac

```bash
bash INICIAR_ASAAS.sh
```

---

## ✅ Resultado Esperado

Terminal mostrará:
```
╔════════════════════════════════════════════════════════════════╗
║    PLATAFORMA ON MEDICINA - ASAAS INTEGRATION v2.0            ║
╚════════════════════════════════════════════════════════════════╝

✅ Python: Python 3.x.x
🚀 Servidor iniciando em http://localhost:5000
```

---

## 🌐 Abrir no Navegador

Acesse: **http://localhost:5000**

---

## 🧪 Testar em Outro Terminal

```powershell
python test_asaas_integration.py
```

Esperado:
```
✅ PASSOU - Connection
✅ PASSOU - Asaas Test
✅ PASSOU - Create Payment
✅ PASSOU - Get Status
✅ PASSOU - Webhook
✅ PASSOU - Confirm Payment

Total: 6/6 testes passaram
🎉 Todos os testes passaram!
```

---

## 📌 Dica para Desenvolvimento Rápido

Se receber erro "comando não encontrado", use `.\` antes:

```powershell
# ❌ Errado
INICIAR_ASAAS.bat

# ✅ Correto
.\INICIAR_ASAAS.bat
```

Isso é uma característica do PowerShell por segurança.

---

## 🔒 Executar com Permissões de Admin (se necessário)

```powershell
# Abrir PowerShell como Administrador
# Depois:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Agora pode executar
.\iniciar.ps1
```

---

**Pronto! Seu sistema Asaas está 100% operacional!** 🚀
