#!/usr/bin/env python3
"""
Script de Testes - Integração Asaas
Testa todos os endpoints e funcionalidades
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
ASAAS_ENDPOINTS = {
    'criar_pagamento': f'{BASE_URL}/api/asaas/criar-pagamento',
    'obter_cobranca': f'{BASE_URL}/api/asaas/obter-cobranca',
    'confirmar_pagamento': f'{BASE_URL}/api/asaas/confirmar-pagamento',
    'status_pagamento': f'{BASE_URL}/api/asaas/status-pagamento',
    'webhook': f'{BASE_URL}/api/asaas/webhook',
    'teste': f'{BASE_URL}/api/asaas/teste'
}

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

def print_step(number, text):
    """Print formatted step"""
    print(f"{Colors.OKCYAN}[STEP {number}]{Colors.ENDC} {text}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def test_connection():
    """Test basic connection to Flask server"""
    print_header("1. Teste de Conexão")
    print_step(1, "Testando conexão com servidor Flask...")
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 404:
            print_success("Servidor Flask está rodando!")
            return True
        else:
            print_success(f"Servidor respondeu com status {response.status_code}")
            return True
    except requests.exceptions.ConnectionError:
        print_error(f"Não conseguiu conectar ao servidor em {BASE_URL}")
        print_info("Inicie o servidor Flask com: python3 app.py")
        return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_asaas_test_endpoint():
    """Test Asaas test endpoint"""
    print_header("2. Teste do Endpoint Asaas")
    print_step(1, "Acessando /api/asaas/teste...")
    
    try:
        response = requests.get(ASAAS_ENDPOINTS['teste'], timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            print_success("Endpoint respondeu com sucesso!")
            print_info(f"Resposta: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Status {response.status_code}: {json.dumps(data, indent=2)}")
            return False
    except Exception as e:
        print_error(f"Erro ao acessar endpoint: {str(e)}")
        return False

def test_create_payment():
    """Test payment creation"""
    print_header("3. Teste de Criação de Pagamento")
    
    test_lead = {
        "lead_id": f"test_lead_{int(time.time())}",
        "lead_name": "João Silva Teste",
        "lead_email": "joao.teste@example.com",
        "lead_cpf": "12345678901234",
        "amount": 100.00
    }
    
    print_step(1, f"Criando pagamento para {test_lead['lead_name']}...")
    print_info(f"Lead: {json.dumps(test_lead, indent=2)}")
    
    try:
        response = requests.post(
            ASAAS_ENDPOINTS['criar_pagamento'],
            json=test_lead,
            timeout=30
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print_success("Pagamento criado com sucesso!")
            
            # Analisar opções de pagamento
            payment_options = data.get('payment_options', {})
            
            print_info("\n📦 Opções de Pagamento Disponíveis:")
            
            if 'pix' in payment_options:
                print_success("PIX disponível")
                pix = payment_options['pix']
                print_info(f"  - Charge ID: {pix.get('charge_id')}")
                print_info(f"  - Valor: R$ {pix.get('value')}")
                print_info(f"  - Status: {pix.get('status')}")
            
            if 'boleto' in payment_options:
                print_success("Boleto disponível")
                boleto = payment_options['boleto']
                print_info(f"  - Charge ID: {boleto.get('charge_id')}")
                print_info(f"  - Valor: R$ {boleto.get('value')}")
                print_info(f"  - Data de Vencimento: {boleto.get('due_date')}")
            
            if 'credit_card' in payment_options:
                print_success("Cartão de Crédito disponível")
                card = payment_options['credit_card']
                print_info(f"  - Charge ID: {card.get('charge_id')}")
                print_info(f"  - Valor: R$ {card.get('value')}")
            
            return True, test_lead, data
        else:
            print_error(f"Erro na criação: {data.get('error', 'Erro desconhecido')}")
            return False, test_lead, data
    
    except Exception as e:
        print_error(f"Erro ao criar pagamento: {str(e)}")
        return False, test_lead, None

def test_get_payment_status(lead_id):
    """Test getting payment status"""
    print_header("4. Teste de Obtenção de Status")
    print_step(1, f"Obtendo status de pagamento para lead {lead_id}...")
    
    try:
        response = requests.get(
            f"{ASAAS_ENDPOINTS['status_pagamento']}/{lead_id}",
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print_success("Status obtido com sucesso!")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Valor: R$ {data.get('amount')}")
            print_info(f"Data de Criação: {data.get('created_at')}")
            return True
        else:
            print_warning(f"Resposta: {json.dumps(data, indent=2)}")
            return False
    
    except Exception as e:
        print_error(f"Erro ao obter status: {str(e)}")
        return False

def test_webhook():
    """Test webhook endpoint"""
    print_header("5. Teste de Webhook")
    
    test_event = {
        "event": "PAYMENT_RECEIVED",
        "charge": {
            "id": "chg_test_123",
            "value": 100.00,
            "status": "RECEIVED"
        }
    }
    
    print_step(1, "Enviando evento de teste para webhook...")
    print_info(f"Evento: {json.dumps(test_event, indent=2)}")
    
    try:
        response = requests.post(
            ASAAS_ENDPOINTS['webhook'],
            json=test_event,
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200:
            print_success("Webhook recebeu evento com sucesso!")
            return True
        else:
            print_warning(f"Resposta: {json.dumps(data, indent=2)}")
            return False
    
    except Exception as e:
        print_error(f"Erro no webhook: {str(e)}")
        return False

def test_confirm_payment(lead_id, charge_id):
    """Test payment confirmation"""
    print_header("6. Teste de Confirmação de Pagamento")
    
    payload = {
        "lead_id": lead_id,
        "charge_id": charge_id
    }
    
    print_step(1, "Confirmando pagamento...")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            ASAAS_ENDPOINTS['confirmar_pagamento'],
            json=payload,
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print_success("Pagamento confirmado com sucesso!")
            return True
        else:
            print_warning(f"Resposta: {json.dumps(data, indent=2)}")
            return False
    
    except Exception as e:
        print_error(f"Erro ao confirmar pagamento: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print_header("TESTES DE INTEGRAÇÃO ASAAS")
    print_info(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"URL Base: {BASE_URL}\n")
    
    results = {
        'connection': False,
        'asaas_test': False,
        'create_payment': False,
        'get_status': False,
        'webhook': False,
        'confirm_payment': False
    }
    
    # Test 1: Connection
    results['connection'] = test_connection()
    if not results['connection']:
        print_error("Não foi possível conectar ao servidor. Abortando testes.")
        return results
    
    time.sleep(1)
    
    # Test 2: Asaas Test Endpoint
    results['asaas_test'] = test_asaas_test_endpoint()
    time.sleep(1)
    
    # Test 3: Create Payment
    success, lead, payment_data = test_create_payment()
    results['create_payment'] = success
    time.sleep(1)
    
    if success and payment_data:
        # Test 4: Get Status
        results['get_status'] = test_get_payment_status(lead['lead_id'])
        time.sleep(1)
        
        # Test 5: Webhook
        results['webhook'] = test_webhook()
        time.sleep(1)
        
        # Test 6: Confirm Payment
        if payment_data.get('payment_options', {}).get('pix'):
            charge_id = payment_data['payment_options']['pix'].get('charge_id')
            results['confirm_payment'] = test_confirm_payment(lead['lead_id'], charge_id)
    
    # Summary
    print_header("RESUMO DOS TESTES")
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        test_label = test_name.replace('_', ' ').title()
        print(f"{status} - {test_label}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} testes passaram{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 Todos os testes passaram!{Colors.ENDC}")
    elif passed >= total * 0.7:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  Alguns testes falharam. Verifique os erros acima.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ Muitos testes falharam. Verifique a configuração.{Colors.ENDC}")
    
    return results

if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Testes interrompidos pelo usuário{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Erro inesperado: {str(e)}{Colors.ENDC}")
