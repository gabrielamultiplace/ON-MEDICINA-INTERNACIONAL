# ⚡ GUIA RÁPIDO DE INICIALIZAÇÃO

## 1️⃣ INSTALAR DEPENDÊNCIAS
```bash
cd "c:\Users\Gabriela Resende\Documents\Plataforma ON"
pip install -r requirements.txt
```

Você vai ver:
```
Successfully installed Flask-3.0.3 Werkzeug-3.0.3 flask-cors-3.0.10
```

---

## 2️⃣ INICIAR A APLICAÇÃO
```bash
python app.py
```

Você vai ver:
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

---

## 3️⃣ ACESSAR NO NAVEGADOR
Abra: **http://localhost:5000**

---

## 4️⃣ FAZER LOGIN
- **Email:** gabrielamultiplace@gmail.com
- **Senha:** @On2025@

---

## ✅ VERIFICAR CONFIGURAÇÃO (Opcional)
```bash
python verify_setup.py
```

---

## 🎯 PRIMEIRA COISA A TESTAR
1. Login com credenciais acima
2. Clicar em **Administrativo** no menu
3. Clicar em **Comercial** → **Acessar Comercial**
4. Clicar em **Novo Lead**
5. Preencher e criar
6. Copiar o link gerado

---

## 📱 TESTE DO FORMULÁRIO DE PACIENTE
Cole o link em uma nova aba e veja o formulário progressivo funcionando!

---

## 🔧 SE HOUVER ERRO

### Erro: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Erro: "Port 5000 already in use"
Mude a porta no final do app.py:
```python
app.run(debug=False, port=5001)  # Usar 5001
```

### Erro: "database is locked"
Delete `data.db` e reinicie:
```bash
del data.db
python app.py
```

---

## 📂 ARQUIVOS IMPORTANTES

| Arquivo | Descrição |
|---------|-----------|
| `app.py` | Backend (Flask) |
| `index.html` | Frontend (HTML/CSS/JS) |
| `data.db` | Banco de dados (SQLite) |
| `data/doctors.json` | Dados de médicos |
| `data/leads.json` | Dados de leads |
| `data/leads_config.json` | Configuração formulário |

---

## 🌐 ACESSOS IMPORTANTES

| URL | Descrição |
|-----|-----------|
| `http://localhost:5000` | Página principal |
| `http://localhost:5000?registerPaciente=0001` | Formulário paciente |
| `http://localhost:5000?registerMedico=true` | Cadastro médico |

---

## 💡 DICAS

✓ Use o verificador: `python verify_setup.py`  
✓ Todos os dados de Kanban são salvos em LocalStorage (persistem)  
✓ Cada módulo é independente  
✓ Links de leads e médicos são públicos e sem autenticação  

---

## ✨ PRONTO!
Sua plataforma está 100% funcional e pronta para uso! 🎉
