# ============================================================================
# ASAAS - Configurações da API
# ============================================================================
# Este arquivo centraliza toda a configuração da integração com Asaas

import os
import json
from datetime import datetime, timedelta

class AsaasConfig:
    """Configuração centralizada para Asaas API"""
    
    # ========== CREDENCIAIS ==========
    API_KEY = os.getenv(
        'ASAAS_API_KEY',
        '$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmNiOGQ2OWQ0LTRkNGMtNDhiYi04M2Q4LTJiZTRmNDk0MDgxMDo6JGFhY2hfYTVhY2NmY2QtNzBlMS00N2FlLWI2YjYtYjFiMzFlN2UyNTNh'
    )
    
    # ========== URLS ==========
    API_BASE_URL = 'https://api.asaas.com/v3'
    SANDBOX_URL = 'https://sandbox.asaas.com/v3'
    WEBHOOK_URL = 'https://app.onmedicinainternacional.com/comercial/webhook-setup'
    
    # ========== CONFIGURAÇÕES DE PAGAMENTO ==========
    PAYMENT_METHODS = {
        'PIX': {
            'enabled': True,
            'description': 'PIX - Transferência instantânea',
            'icon': 'qrcode',
            'fee': 0  # 0% de taxa para PIX
        },
        'BOLETO': {
            'enabled': True,
            'description': 'Boleto - Pagamento tradicional',
            'icon': 'barcode',
            'fee': 0.8  # 0.8% de taxa
        },
        'CREDIT_CARD': {
            'enabled': True,
            'description': 'Cartão de Crédito',
            'icon': 'credit-card',
            'fee': 2.99  # 2.99% de taxa
        }
    }
    
    # ========== PRAZOS ==========
    DUE_DATE_DAYS = 30  # Dias para vencimento padrão
    PIX_EXPIRATION_MINUTES = 60  # PIX expira em 60 minutos
    
    # ========== WEBHOOKS ==========
    WEBHOOK_EVENTS = [
        'PAYMENT_RECEIVED',      # Pagamento recebido
        'PAYMENT_CONFIRMED',     # Pagamento confirmado
        'PAYMENT_PENDING',       # Pagamento pendente
        'PAYMENT_FAILED',        # Pagamento falhou
        'PAYMENT_OVERDUE',       # Pagamento em atraso
        'INVOICE_CREATED',       # Cobrança criada
        'INVOICE_UPDATED',       # Cobrança atualizada
        'INVOICE_DELETED'        # Cobrança deletada
    ]
    
    # ========== MODO DE OPERAÇÃO ==========
    USE_SANDBOX = os.getenv('ASAAS_SANDBOX', 'false').lower() == 'true'  # Use sandbox por padrão em dev
    FALLBACK_MODE = True  # Modo demo se Asaas não responder
    
    @classmethod
    def get_api_url(cls):
        """Retorna a URL base da API (sandbox ou produção)"""
        return cls.SANDBOX_URL if cls.USE_SANDBOX else cls.API_BASE_URL
    
    @classmethod
    def get_headers(cls):
        """Retorna headers padrão para requisições Asaas"""
        return {
            'access_token': cls.API_KEY,
            'Content-Type': 'application/json'
        }
    
    @classmethod
    def calculate_due_date(cls):
        """Calcula data de vencimento (hoje + DUE_DATE_DAYS)"""
        return (datetime.now() + timedelta(days=cls.DUE_DATE_DAYS)).strftime('%Y-%m-%d')
    
    @classmethod
    def get_enabled_methods(cls):
        """Retorna apenas os métodos de pagamento habilitados"""
        return {
            method: config 
            for method, config in cls.PAYMENT_METHODS.items() 
            if config['enabled']
        }
    
    @classmethod
    def validate_api_key(cls):
        """Valida se a API key está configurada"""
        if not cls.API_KEY or cls.API_KEY == '$aact_prod_...':
            raise ValueError(
                'API Key do Asaas não configurada. '
                'Defina a variável de ambiente ASAAS_API_KEY'
            )
        return True


class WebhookConfig:
    """Configuração de webhooks Asaas"""
    
    # Mapeamento de eventos para ações
    EVENT_HANDLERS = {
        'PAYMENT_RECEIVED': 'on_payment_received',
        'PAYMENT_CONFIRMED': 'on_payment_confirmed',
        'PAYMENT_FAILED': 'on_payment_failed',
        'PAYMENT_OVERDUE': 'on_payment_overdue'
    }
    
    # Chave para validar assinatura de webhook
    WEBHOOK_SECRET = os.getenv('ASAAS_WEBHOOK_SECRET', 'webhook_secret_key')
    
    @classmethod
    def validate_signature(cls, request_data, signature):
        """Valida assinatura do webhook do Asaas"""
        import hashlib
        import hmac
        
        # Computar HMAC
        body = json.dumps(request_data, separators=(',', ':'), sort_keys=True)
        expected_signature = hmac.new(
            cls.WEBHOOK_SECRET.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)


class PaymentDefaults:
    """Padrões de pagamento"""
    
    # Dados padrão para teste
    TEST_CUSTOMER = {
        'name': 'Cliente Teste',
        'email': 'teste@example.com',
        'cpfCnpj': '12345678901234'
    }
    
    TEST_CHARGE = {
        'billingType': 'BOLETO',
        'value': 100.00,
        'description': 'Serviço Médico'
    }
    
    @classmethod
    def get_customer_data(cls, lead):
        """Prepara dados de cliente a partir de um lead"""
        return {
            'name': lead.get('name', 'Cliente').strip(),
            'email': lead.get('email', 'noreply@onmedicina.com').strip(),
            'cpfCnpj': cls._sanitize_cpf(lead.get('cpf', '12345678901234')),
            'phone': lead.get('phone', '').strip(),
            'city': lead.get('city', '').strip(),
            'state': lead.get('state', '').strip()
        }
    
    @staticmethod
    def _sanitize_cpf(cpf):
        """Remove caracteres especiais do CPF"""
        if not cpf:
            return '12345678901234'
        return ''.join(c for c in cpf if c.isdigit())[:14]


# ============================================================================
# ENDPOINTS ASAAS
# ============================================================================

ASAAS_ENDPOINTS = {
    # Clientes
    'create_customer': '/customers',
    'list_customers': '/customers',
    'get_customer': '/customers/{id}',
    'update_customer': '/customers/{id}',
    'delete_customer': '/customers/{id}',
    
    # Cobranças/Invoices
    'create_charge': '/charges',
    'list_charges': '/charges',
    'get_charge': '/charges/{id}',
    'update_charge': '/charges/{id}',
    'delete_charge': '/charges/{id}',
    'restore_charge': '/charges/{id}/restore',
    
    # Pagamentos
    'confirm_payment': '/charges/{id}/confirm',
    'refund_payment': '/charges/{id}/refund',
    
    # Webhooks
    'create_webhook': '/webhooks',
    'list_webhooks': '/webhooks',
    'get_webhook': '/webhooks/{id}',
    'delete_webhook': '/webhooks/{id}',
    'test_webhook': '/webhooks/{id}/test'
}


# ============================================================================
# TEMPLATE DE RESPOSTA PADRÃO
# ============================================================================

DEFAULT_RESPONSE_TEMPLATE = {
    'success': False,
    'error': None,
    'data': None,
    'timestamp': datetime.now().isoformat(),
    'source': 'asaas_api'
}


if __name__ == '__main__':
    # ========== TESTE DE CONFIGURAÇÃO ==========
    print('✅ Asaas Configuration Loaded')
    print(f'API URL: {AsaasConfig.get_api_url()}')
    print(f'Sandbox Mode: {AsaasConfig.USE_SANDBOX}')
    print(f'Payment Methods: {list(AsaasConfig.get_enabled_methods().keys())}')
    print(f'Webhook Events: {len(WebhookConfig.EVENT_HANDLERS)} handlers')
