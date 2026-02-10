#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import app

client = app.test_client()

print("=" * 70)
print("TESTE: Configuração de Webhook Asaas")
print("=" * 70)

# Test 1: Webhook Config
print("\n1. GET /api/asaas/webhook-config")
r = client.get('/api/asaas/webhook-config')
data = r.get_json()
print(f"   Status: {r.status_code}")
print(f"   Webhook URL: {data.get('webhook_url')}")
print(f"   API Key Status: {data.get('api_key', {}).get('status')}")
print(f"   API Key (masked): {data.get('api_key', {}).get('masked')}")
print(f"   Environment: {data.get('api_key', {}).get('environment')}")
print(f"   Events count: {len(data.get('events', []))}")
print(f"   Base URL: {data.get('api_key', {}).get('base_url')}")

# Test 2: Validar Token
print("\n2. GET /api/asaas/validar-token")
r2 = client.get('/api/asaas/validar-token')
data2 = r2.get_json()
print(f"   Status: {r2.status_code}")
print(f"   Valid: {data2.get('valid')}")
print(f"   Message: {data2.get('message')}")
print(f"   Token Status: {data2.get('status')}")

print("\n" + "=" * 70)
print("RESUMO:")
print("=" * 70)
if r.status_code == 200:
    print("✅ Webhook Config - OK")
else:
    print("❌ Webhook Config - ERRO")

if data.get('api_key', {}).get('status') == '✅ Configurado':
    print("✅ Token Asaas - CONFIGURADO")
else:
    print("❌ Token Asaas - NÃO CONFIGURADO")

print("\n🎯 Token mascarado:", data.get('api_key', {}).get('masked'))
print("🔐 Ambiente:", data.get('api_key', {}).get('environment'))
print("\n✅ Configuração concluída com sucesso!")
