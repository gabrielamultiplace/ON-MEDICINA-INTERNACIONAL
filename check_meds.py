import sqlite3
import json

print("=" * 60)
print("VERIFICAÇÃO DE MEDICAMENTOS")
print("=" * 60)

try:
    # Verificar banco de dados
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Listar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\nTabelas no banco de dados:")
    for t in tables:
        cursor.execute(f'SELECT COUNT(*) FROM [{t[0]}]')
        count = cursor.fetchone()[0]
        print(f'  - {t[0]}: {count} registros')
    
    # Se existe tabela de medicamentos, verificar duplicados
    if any('medic' in t[0].lower() for t in tables):
        med_table = next(t[0] for t in tables if 'medic' in t[0].lower())
        print(f"\nVerificando tabela: {med_table}")
        
        cursor.execute(f"SELECT COUNT(*) FROM [{med_table}]")
        total = cursor.fetchone()[0]
        print(f"Total de medicamentos: {total}")
        
        # Encontrar duplicados
        cursor.execute(f"SELECT COUNT(DISTINCT nome) FROM [{med_table}]")
        distintos = cursor.fetchone()[0]
        print(f"Nomes únicos: {distintos}")
        
        if total > distintos:
            print(f"\n⚠️  {total - distintos} registros duplicados encontrados!")
            
            cursor.execute(f"""
            SELECT nome, COUNT(*) as qtd 
            FROM [{med_table}]
            GROUP BY nome 
            HAVING COUNT(*) > 1
            ORDER BY qtd DESC
            LIMIT 20
            """)
            
            dups = cursor.fetchall()
            print("\nMedicamentos duplicados:")
            for nome, qtd in dups:
                print(f'  {nome}: {qtd}x')
    
    conn.close()
    
except Exception as e:
    print(f"Erro ao acessar banco: {e}")

# Verificar arquivo JSON
print("\n" + "-" * 60)
try:
    with open('data/medicamentos.json', 'r', encoding='utf-8') as f:
        meds_json = json.load(f)
    print(f"medicamentos.json: {len(meds_json)} medicamentos")
except Exception as e:
    print(f"medicamentos.json não encontrado ou erro: {e}")

print("=" * 60)
