import requests
import json

print("🔍 Testando endpoint de medicamentos...")
try:
    resp = requests.get('http://localhost:5000/api/debug/medicamentos')
    data = resp.json()
    print(f"✅ Status: {resp.status_code}")
    print(f"📊 Total medicamentos: {data['total']}")
    print(f"📁 Arquivo existe: {data['file_exists']}")
    print(f"📏 Tamanho: {data['file_size']} bytes")
    if data['sample']:
        print(f"🏥 Primeiro medicamento: {data['sample'][0]['nome']}")
except Exception as e:
    print(f"❌ Erro: {e}")
