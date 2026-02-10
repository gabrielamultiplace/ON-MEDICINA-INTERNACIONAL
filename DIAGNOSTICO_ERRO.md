# 🔧 DIAGNÓSTICO: CONEXÃO LOCALHOST RECUSADA

## ❌ PROBLEMA
```
A conexão com localhost:5000 foi recusada
```

---

## 🔍 CAUSAS POSSÍVEIS

### **1. Servidor Flask não foi iniciado**
✓ Solução: Execute `python app.py` no prompt

### **2. Python não está instalado**
✓ Solução: Baixe em python.org e instale

### **3. Dependências não instaladas**
✓ Solução: Execute `pip install -r requirements.txt`

### **4. Porta 5000 em uso por outro programa**
✓ Solução: Mude a porta em app.py (linha 522)

### **5. Firewall bloqueando**
✓ Solução: Libere localhost:5000 no firewall

---

## ✅ SOLUÇÃO PASSO A PASSO

### PASSO 1: Verificar se Python está instalado
```bash
python --version
```
Deve mostrar: Python 3.x.x

Se não funcionar:
- Baixe Python em: https://python.org
- Instale marcando: "Add Python to PATH"


### PASSO 2: Instalar dependências
```bash
pip install -r requirements.txt
```

Espere até aparecer: "Successfully installed..."


### PASSO 3: Verificar arquivos necessários

Certifique-se que existem:
- ✅ app.py
- ✅ index.html
- ✅ requirements.txt
- ✅ data.db
- ✅ data/ (pasta)


### PASSO 4: Iniciar servidor

```bash
cd "c:\Users\Gabriela Resende\Documents\Plataforma ON"
python app.py
```

**Você deve ver algo assim:**

```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```


### PASSO 5: Acessar no navegador

Abra uma **nova janela do navegador** e cole:

```
http://localhost:5000
```


### PASSO 6: Fazer login

```
Email: gabrielamultiplace@gmail.com
Senha: @On2025@
```

---

## 🆘 SE AINDA NÃO FUNCIONAR

### Erro: "Port 5000 already in use"

A porta 5000 está sendo usada por outro programa.

**Solução:**

1. Abra `app.py` com editor de texto
2. Vá para a **última linha (522)**
3. Mude:
```python
app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)
```

Para:
```python
app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5001)
```

4. Salve o arquivo
5. Rode: `python app.py`
6. Acesse: `http://localhost:5001`


### Erro: "No module named 'flask'"

Dependências não foram instaladas.

**Solução:**
```bash
pip install -r requirements.txt
```

Espere completar (pode demorar alguns minutos).


### Erro: "ModuleNotFoundError"

Algum módulo está faltando.

**Solução:**
```bash
pip install Flask==3.0.3
pip install Werkzeug==3.0.3
pip install flask-cors==3.0.10
```


### Erro: "Database is locked"

O banco SQLite está travado.

**Solução:**
1. Delete o arquivo `data.db`
2. Rode: `python app.py`
3. O banco será recriado automaticamente

---

## 📋 CHECKLIST DE VERIFICAÇÃO

- [ ] Python instalado? (`python --version` funciona)
- [ ] Dependências instaladas? (`pip install -r requirements.txt` funcionou)
- [ ] Arquivos existem? (`app.py`, `index.html`, etc.)
- [ ] Servidor rodando? (ver mensagem "Running on...")
- [ ] Navegador acessando? (http://localhost:5000)
- [ ] Login funcionando? (credenciais corretas)

---

## 🚀 COMANDO COMPLETO (COPIE E COLE)

Abra o Prompt de Comando e cole isto:

```bash
cd "c:\Users\Gabriela Resende\Documents\Plataforma ON" && pip install -r requirements.txt && python app.py
```

Depois abra no navegador:
```
http://localhost:5000
```

---

## 📞 ÚLTIMO RECURSO

Se nada funcionar:

1. Delete a pasta `data`
2. Delete o arquivo `data.db`
3. Rode novamente: `python app.py`
4. Acesse: `http://localhost:5000`

O banco será recriado com valores padrão.

---

**Qualquer erro, compartilhe a mensagem que aparecer no prompt que corrijo! 💪**
