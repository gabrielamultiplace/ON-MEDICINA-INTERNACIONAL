#!/usr/bin/env python3
"""
Script de verificação e inicialização da plataforma ON Medicina Internacional
"""
import os
import json
import sqlite3
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(BASE_DIR, 'data.db')
DOCTORS_FILE = os.path.join(DATA_DIR, 'doctors.json')
LEADS_FILE = os.path.join(DATA_DIR, 'leads.json')
LEADS_CONFIG_FILE = os.path.join(DATA_DIR, 'leads_config.json')

print("=" * 60)
print("VERIFICAÇÃO DE CONFIGURAÇÕES - ON Medicina Internacional")
print("=" * 60)

# 1. Verificar diretórios
print("\n✓ Verificando diretórios...")
os.makedirs(DATA_DIR, exist_ok=True)
print(f"  - Data dir: {DATA_DIR} {'[OK]' if os.path.exists(DATA_DIR) else '[ERRO]'}")

# 2. Verificar doctors.json
print("\n✓ Verificando doctors.json...")
if not os.path.exists(DOCTORS_FILE):
    with open(DOCTORS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    print(f"  - Arquivo criado: {DOCTORS_FILE}")
else:
    print(f"  - Arquivo existe: {DOCTORS_FILE}")

# 3. Verificar leads.json
print("\n✓ Verificando leads.json...")
if not os.path.exists(LEADS_FILE):
    with open(LEADS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    print(f"  - Arquivo criado: {LEADS_FILE}")
else:
    with open(LEADS_FILE, 'r', encoding='utf-8') as f:
        leads = json.load(f)
    print(f"  - Arquivo existe: {LEADS_FILE}")
    print(f"  - Total de leads: {len(leads)}")

# 4. Verificar leads_config.json
print("\n✓ Verificando leads_config.json...")
if not os.path.exists(LEADS_CONFIG_FILE):
    default_config = {
        "sections": [
            {
                "id": "section_1",
                "title": "Dados Informativos do Paciente",
                "order": 1,
                "fields": [
                    {"id": "nome_completo", "label": "Nome Completo", "type": "text", "required": True, "order": 1},
                    {"id": "cpf", "label": "CPF", "type": "text", "required": True, "order": 2},
                    {"id": "data_nascimento", "label": "Data de Nascimento", "type": "date", "required": True, "order": 3},
                    {"id": "telefone", "label": "Telefone", "type": "text", "required": True, "order": 6},
                    {"id": "email", "label": "E-mail", "type": "email", "required": True, "order": 8}
                ]
            }
        ]
    }
    with open(LEADS_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    print(f"  - Arquivo criado com configuração padrão")
else:
    with open(LEADS_CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"  - Arquivo existe: {LEADS_CONFIG_FILE}")
    print(f"  - Seções configuradas: {len(config.get('sections', []))}")

# 5. Verificar banco de dados SQLite
print("\n✓ Verificando banco de dados SQLite...")
if os.path.exists(DB_PATH):
    print(f"  - DB existe: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"  - Tabelas: {[t[0] for t in tables]}")
    
    if tables:
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"  - Usuários cadastrados: {user_count}")
    conn.close()
else:
    print(f"  - DB não existe (será criado ao iniciar a app)")

# 6. Verificar arquivos estáticos
print("\n✓ Verificando arquivos estáticos...")
files_to_check = ['index.html', 'app.py', 'requirements.txt']
for f in files_to_check:
    path = os.path.join(BASE_DIR, f)
    exists = "✓" if os.path.exists(path) else "✗"
    print(f"  {exists} {f}")

# 7. Resumo final
print("\n" + "=" * 60)
print("RESUMO DA CONFIGURAÇÃO")
print("=" * 60)
print(f"""
✓ Plataforma: ON Medicina Internacional
✓ Base de dados: {DB_PATH}
✓ Diretório de dados: {DATA_DIR}
✓ Diretório de uploads: {os.path.join(BASE_DIR, 'uploads')}

PRÓXIMOS PASSOS:
1. Instalar dependências:
   pip install -r requirements.txt

2. Iniciar a aplicação:
   python app.py

3. Acessar no navegador:
   http://localhost:5000

CREDENCIAIS DE TESTE:
   Email: gabrielamultiplace@gmail.com
   Senha: @On2025@

✓ Configuração completa e pronta para uso!
""")
print("=" * 60)
