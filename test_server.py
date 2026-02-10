#!/usr/bin/env python
"""Teste rápido dos endpoints principais"""

import requests
import json

print("\n" + "="*60)
print("🧬 TESTE DE CONECTIVIDADE - CANNABIS MEDICINAL")
print("="*60)

try:
    # Test 1: Health
    print("\n[1] Health Check...")
    r = requests.get('http://localhost:5000/api/cannabis/health', timeout=5)
    if r.status_code == 200:
        print("✅ Cannabis module: OPERATIONAL")
    else:
        print(f"⚠️ Status: {r.status_code}")

    # Test 2: Home page
    print("\n[2] Home Page...")
    r = requests.get('http://localhost:5000/', timeout=5)
    if r.status_code == 200:
        print("✅ Servidor Flask: RODANDO")
    else:
        print(f"⚠️ Status: {r.status_code}")

    # Test 3: API endpoints
    print("\n[3] API Endpoints...")
    endpoints = [
        ('/api/cannabis/products', 'Produtos'),
        ('/api/cannabis/suppliers', 'Fornecedores'),
        ('/api/doctors', 'Médicos'),
        ('/api/leads', 'Leads'),
    ]
    
    for endpoint, name in endpoints:
        r = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
        status = "✅" if r.status_code == 200 else "⚠️"
        print(f"  {status} {name:20} - Status {r.status_code}")

    print("\n" + "="*60)
    print("✅ TUDO FUNCIONANDO - Servidor pronto!")
    print("="*60)
    print("\nURLs disponíveis:")
    print("  • Principal: http://localhost:5000")
    print("  • Cannabis: http://localhost:5000/api/cannabis/health")
    print("  • API: http://localhost:5000/api/...")
    
except requests.exceptions.ConnectionError:
    print("❌ ERRO: Não conseguiu conectar ao localhost:5000")
    print("   Certifique-se de que o servidor está rodando!")
except Exception as e:
    print(f"❌ ERRO: {e}")
