#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test login with session persistence"""

import requests
from requests.cookies import RequestsCookieJar

BASE_URL = 'http://localhost:5000'

def test_login_with_session():
    """Test login endpoint with session"""
    print("=" * 60)
    print("TESTE DE LOGIN COM SESSÃO")
    print("=" * 60)
    
    # Create a session to persist cookies
    session = requests.Session()
    
    # Test 1: Login
    print("\n1. Fazendo login...")
    data = {
        'email': 'gabrielamultiplace@gmail.com',
        'password': '@On2025@'
    }
    
    try:
        response = session.post(f'{BASE_URL}/api/login', json=data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Login bem-sucedido!")
            print(f"   Cookies: {session.cookies}")
            print(f"   Usuário: {result.get('user', {}).get('name')}")
            print(f"   Headers da resposta: {dict(response.headers)}")
        else:
            print(f"   ✗ Login falhou! Response: {response.text}")
            
    except Exception as e:
        print(f"   ✗ Erro: {e}")
        return
    
    # Test 2: Verificar sessão com /api/me
    print("\n2. Verificando sessão com /api/me...")
    try:
        response = session.get(f'{BASE_URL}/api/me')
        print(f"   Status: {response.status_code}")
        print(f"   Cookies enviados: {session.cookies}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Sessão válida!")
            print(f"   Usuário: {result.get('user', {}).get('name')}")
        else:
            print(f"   ✗ Sessão inválida! Response: {response.text}")
            
    except Exception as e:
        print(f"   ✗ Erro: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_login_with_session()
