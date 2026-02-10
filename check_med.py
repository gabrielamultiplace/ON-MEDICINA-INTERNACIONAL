import json
import os

med_file = 'data/medicamentos.json'
print(f"Arquivo existe: {os.path.exists(med_file)}")
print(f"Tamanho: {os.path.getsize(med_file)} bytes")

with open(med_file) as f:
    data = json.load(f)
    
print(f"Total medicamentos: {len(data)}")
if data:
    print(f"Primeiro: {data[0]['nome']}")
    print(f"Último: {data[-1]['nome']}")
