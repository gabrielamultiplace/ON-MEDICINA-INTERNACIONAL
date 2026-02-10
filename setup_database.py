#!/usr/bin/env python3
import sqlite3
from werkzeug.security import generate_password_hash

# Tentar se conectar ao banco
db_path = "data.db"

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Ver se a tabela users existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    exists = cursor.fetchone()
    
    if not exists:
        print("❌ Tabela 'users' não existe. Criando...")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
        print("✅ Tabela criada!")
    else:
        print("✅ Tabela 'users' existe")
    
    # Verificar se há usuários
    cursor.execute("SELECT COUNT(*) as count FROM users")
    count = cursor.fetchone()['count']
    print(f"📊 Total de usuários: {count}")
    
    # Verificar usuário admin
    cursor.execute("SELECT * FROM users WHERE email = ?", ("gabrielamultiplace@gmail.com",))
    admin = cursor.fetchone()
    
    if admin:
        print(f"✅ Usuário admin existe: {admin['name']} ({admin['email']})")
    else:
        print("❌ Usuário admin não existe. Criando...")
        from datetime import datetime, timezone
        admin_email = "gabrielamultiplace@gmail.com"
        admin_password = "@On2025@"
        
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Gabriela Admin",
            admin_email,
            generate_password_hash(admin_password),
            "admin",
            datetime.now(timezone.utc).isoformat(),
        ))
        conn.commit()
        print(f"✅ Usuário admin criado!")
        print(f"   Email: {admin_email}")
        print(f"   Senha: {admin_password}")
    
    conn.close()
    print("\n✅ Banco de dados verificado com sucesso!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
