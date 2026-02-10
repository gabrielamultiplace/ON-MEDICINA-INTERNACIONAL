#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test login functionality"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_login():
    """Test login endpoint"""
    print("=" * 60)
    print("TESTE DE LOGIN")
    print("=" * 60)
    
    # Test 1: Valid credentials
    print("\n1. Testando com credenciais válidas...")
    data = {
        'email': 'gabrielamultiplace@gmail.com',
        'password': '@On2025@'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/login', json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Login bem-sucedido!")
            print(f"   Usuário: {result.get('user', {}).get('name')}")
        else:
            print(f"   ✗ Login falhou!")
            
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    # Test 2: Invalid password
    print("\n2. Testando com senha inválida...")
    data = {
        'email': 'gabrielamultiplace@gmail.com',
        'password': 'senha_errada'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/login', json=data)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ✓ Corretamente rejeitado")
        else:
            print(f"   ✗ Deveria ter rejeitado!")
            
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    # Test 3: Missing credentials
    print("\n3. Testando sem credenciais...")
    try:
        response = requests.post(f'{BASE_URL}/api/login', json={})
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ✓ Corretamente rejeitado")
        else:
            print(f"   ✗ Deveria ter rejeitado!")
            
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    # Test 4: Check /api/me without session
    print("\n4. Testando /api/me sem sessão...")
    try:
        response = requests.get(f'{BASE_URL}/api/me')
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ✓ Corretamente rejeitado (não autenticado)")
        else:
            print(f"   ✗ Deveria ter rejeitado!")
            
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_login()
