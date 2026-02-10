#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste simples de login - simula comportamento do navegador"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_complete_flow():
    """Simula o fluxo completo de login"""
    print("=" * 70)
    print("TESTE COMPLETO DE LOGIN")
    print("=" * 70)
    
    # Criar uma sessão para manter cookies
    session = requests.Session()
    
    # ETAPA 1: Verificar /api/me sem autenticação
    print("\n[1] Verificando /api/me sem autenticação...")
    try:
        r = session.get(f'{BASE_URL}/api/me')
        print(f"    Status: {r.status_code}")
        if r.status_code != 200:
            print(f"    ✓ Correto - Não autenticado (status {r.status_code})")
        else:
            print(f"    ✗ Erro - Deveria estar não autenticado")
    except Exception as e:
        print(f"    ✗ Erro de conexão: {e}")
        return
    
    # ETAPA 2: Fazer login
    print("\n[2] Fazendo login com credenciais corretas...")
    login_data = {
        'email': 'gabrielamultiplace@gmail.com',
        'password': '@On2025@'
    }
    
    try:
        r = session.post(f'{BASE_URL}/api/login', json=login_data)
        print(f"    Status: {r.status_code}")
        
        if r.status_code == 200:
            result = r.json()
            print(f"    ✓ Login bem-sucedido!")
            print(f"    Usuário: {result.get('user', {}).get('name')}")
            print(f"    Email: {result.get('user', {}).get('email')}")
            print(f"    Cookies na sessão: {list(session.cookies)}")
        else:
            print(f"    ✗ Login falhou!")
            print(f"    Response: {r.text}")
            return
    except Exception as e:
        print(f"    ✗ Erro: {e}")
        return
    
    # ETAPA 3: Verificar /api/me COM autenticação
    print("\n[3] Verificando /api/me COM autenticação...")
    time.sleep(0.5)
    try:
        r = session.get(f'{BASE_URL}/api/me')
        print(f"    Status: {r.status_code}")
        print(f"    Cookies enviados: {list(session.cookies)}")
        
        if r.status_code == 200:
            result = r.json()
            print(f"    ✓ Sessão válida!")
            print(f"    Usuário: {result.get('user', {}).get('name')}")
        else:
            print(f"    ✗ Sessão inválida!")
            print(f"    Response: {r.text}")
    except Exception as e:
        print(f"    ✗ Erro: {e}")
    
    # ETAPA 4: Fazer logout
    print("\n[4] Fazendo logout...")
    try:
        r = session.post(f'{BASE_URL}/api/logout')
        print(f"    Status: {r.status_code}")
        if r.status_code == 200:
            print(f"    ✓ Logout bem-sucedido!")
        else:
            print(f"    ✗ Logout falhou!")
    except Exception as e:
        print(f"    ✗ Erro: {e}")
    
    # ETAPA 5: Verificar /api/me após logout
    print("\n[5] Verificando /api/me após logout...")
    time.sleep(0.5)
    try:
        r = session.get(f'{BASE_URL}/api/me')
        print(f"    Status: {r.status_code}")
        
        if r.status_code != 200:
            print(f"    ✓ Correto - Sessão encerrada (status {r.status_code})")
        else:
            print(f"    ✗ Erro - Ainda autenticado após logout!")
    except Exception as e:
        print(f"    ✗ Erro: {e}")
    
    print("\n" + "=" * 70)
    print("TESTE CONCLUÍDO")
    print("=" * 70)

if __name__ == '__main__':
    test_complete_flow()
