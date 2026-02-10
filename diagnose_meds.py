import json
import os

print("\n" + "="*70)
print("DIAGNÓSTICO - MEDICAMENTOS")
print("="*70)

# Verificar tamanho do arquivo
size = os.path.getsize('data/medicamentos.json')
print(f'\nTamanho do arquivo: {size} bytes')

# Contar medicamentos
with open('data/medicamentos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total de medicamentos: {len(data)}')

# Verificar se há duplicados por nome
nomes = [m.get('nome', '') for m in data]
unicos = len(set(nomes))

print(f'Nomes únicos: {unicos}')
print(f'Duplicados: {len(nomes) - unicos}')

# Se tem muitos, mostrar alguns
if len(data) > 20:
    print(f'\nPrimeiros 5 medicamentos:')
    for i, m in enumerate(data[:5]):
        print(f'  {i+1}. {m.get("nome", "SEM NOME")}')
    print(f'\n  ...')
    print(f'\nÚltimos 5 medicamentos:')
    for i, m in enumerate(data[-5:], start=len(data)-4):
        print(f'  {i}. {m.get("nome", "SEM NOME")}')
    
    print(f'\n' + "="*70)
    print("⚠️  DETECTADO: Arquivo com {0} medicamentos em vez de 20!".format(len(data)))
    print("="*70)
