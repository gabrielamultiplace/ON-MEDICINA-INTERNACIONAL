import requests
import json

resp = requests.get('http://localhost:5000/api/medicamentos')
data = resp.json()

print(f"📊 Total de medicamentos retornados: {len(data)}")
print("\n📋 Lista de medicamentos:")
for i, med in enumerate(data, 1):
    print(f"{i:2d}. {med.get('nome')} (ID: {med.get('id')})")

print(f"\n✅ API funcionando corretamente com {len(data)} medicamentos")
