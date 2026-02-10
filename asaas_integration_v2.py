"""
Integração com API Asaas - Versão 2.0
Pagamentos PIX, Boleto, Cartão de Crédito
Documentação: https://docs.asaas.com/
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações da API Asaas
API_KEY = "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmNiOGQ2OWQ0LTRkNGMtNDhiYi04M2Q4LTJiZTRmNDk0MDgxMDo6JGFhY2hfYTVhY2NmY2QtNzBlMS00N2FlLWI2YjYtYjFiMzFlN2UyNTNh"
API_BASE_URL = "https://api.asaas.com/v3"
SANDBOX_URL = "https://sandbox.asaas.com/v3"
USE_SANDBOX = False  # Mude para True para ambiente de testes
WEBHOOK_URL = "https://app.onmedicinainternacional.com/comercial/webhook-setup"


class AsaasIntegration:
    """
    Classe para integração com API Asaas
    Suporta PIX, Boleto e Cartão de Crédito
    """
    
    def __init__(self, api_key: str = None, sandbox: bool = None):
        """
        Inicializa a integração com Asaas
        
        Args:
            api_key: Chave da API Asaas (padrão: variável global API_KEY)
            sandbox: Se True, usa ambiente de testes (padrão: USE_SANDBOX)
        """
        self.api_key = api_key or API_KEY
        self.sandbox = sandbox if sandbox is not None else USE_SANDBOX
        self.base_url = SANDBOX_URL if self.sandbox else API_BASE_URL
        
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "access_token": self.api_key
        }
        
        logger.info(f"🔗 AsaasIntegration inicializado")
        logger.info(f"   URL: {self.base_url}")
        logger.info(f"   Sandbox: {self.sandbox}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        timeout: int = 10
    ) -> Dict:
        """
        Realiza uma requisição HTTP na API Asaas
        
        Args:
            method: GET, POST, PUT, DELETE
            endpoint: Endpoint da API (ex: /charges)
            data: Dados para POST/PUT
            timeout: Timeout em segundos
            
        Returns:
            Resposta em formato JSON ou dicionário de erro
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"📤 {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=timeout)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=timeout)
            else:
                raise ValueError(f"Método HTTP {method} não suportado")
            
            logger.info(f"📥 Status: {response.status_code}")
            
            # Tratamento de erros
            if response.status_code >= 400:
                error_msg = response.text
                logger.error(f"❌ Erro ({response.status_code}): {error_msg}")
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": error_msg,
                    "endpoint": endpoint
                }
            
            # Retornar resposta
            if response.text:
                return response.json()
            else:
                return {"success": True}
        
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout na requisição para {endpoint}")
            return {"error": True, "message": "Timeout na requisição"}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"⚠️ Erro na requisição: {str(e)}")
            return {"error": True, "message": str(e)}
    
    # ========== CLIENTES ==========
    
    def criar_cliente(
        self,
        name: str,
        email: str,
        cpf_cnpj: str,
        phone: str = None,
        city: str = None,
        state: str = None,
        address: str = None
    ) -> Dict:
        """
        Cria um cliente no Asaas
        
        Args:
            name: Nome do cliente
            email: Email do cliente
            cpf_cnpj: CPF/CNPJ do cliente
            phone: Telefone (opcional)
            city: Cidade (opcional)
            state: Estado (opcional)
            address: Endereço (opcional)
            
        Returns:
            Dicionário com dados do cliente criado
        """
        customer_data = {
            "name": name.strip() if name else "Cliente",
            "email": email.strip() if email else "noreply@onmedicina.com",
            "cpfCnpj": self._sanitize_cpf(cpf_cnpj)
        }
        
        if phone and phone.strip():
            customer_data["phone"] = phone.strip()
        if city and city.strip():
            customer_data["city"] = city.strip()
        if state and state.strip():
            customer_data["state"] = state.strip()
        if address and address.strip():
            customer_data["address"] = address.strip()
        
        logger.info(f"👤 Criando cliente: {name}")
        return self._make_request("POST", "/customers", customer_data)
    
    def listar_clientes(self) -> Dict:
        """Lista todos os clientes"""
        logger.info("📋 Listando clientes...")
        return self._make_request("GET", "/customers")
    
    def obter_cliente(self, customer_id: str) -> Dict:
        """Obtém dados de um cliente específico"""
        return self._make_request("GET", f"/customers/{customer_id}")
    
    def atualizar_cliente(self, customer_id: str, data: Dict) -> Dict:
        """Atualiza dados de um cliente"""
        return self._make_request("PUT", f"/customers/{customer_id}", data)
    
    def deletar_cliente(self, customer_id: str) -> Dict:
        """Deleta um cliente"""
        return self._make_request("DELETE", f"/customers/{customer_id}")
    
    # ========== COBRANÇAS ==========
    
    def criar_cobranca(
        self,
        customer_id: str = None,
        name: str = None,
        email: str = None,
        cpf_cnpj: str = None,
        amount: float = 0.0,
        description: str = None,
        due_date: str = None,
        billing_type: str = "PIX"
    ) -> Dict:
        """
        Cria uma cobrança (charge) no Asaas
        
        Args:
            customer_id: ID do cliente (se já existe)
            name: Nome do cliente (se não existe)
            email: Email do cliente (se não existe)
            cpf_cnpj: CPF/CNPJ do cliente (se não existe)
            amount: Valor da cobrança
            description: Descrição da cobrança
            due_date: Data de vencimento (YYYY-MM-DD)
            billing_type: PIX, BOLETO ou CREDIT_CARD
            
        Returns:
            Dicionário com dados da cobrança criada
        """
        
        # Se não tiver customer_id, criar cliente
        if not customer_id:
            customer_result = self.criar_cliente(
                name=name or "Cliente",
                email=email or "noreply@onmedicina.com",
                cpf_cnpj=cpf_cnpj or "12345678901234",
                phone=None,
                city=None,
                state=None
            )
            
            if customer_result.get("error"):
                return customer_result
            
            customer_id = customer_result.get("id")
        
        # Preparar dados da cobrança
        charge_data = {
            "customer": customer_id,
            "billingType": billing_type,
            "value": float(amount),
            "description": description or "Serviço Médico ON",
            "dueDate": due_date or self._get_due_date()
        }
        
        # Configurações específicas para PIX
        if billing_type == "PIX":
            charge_data["pixExpirationMinutes"] = 60
        
        logger.info(f"💰 Criando cobrança: {billing_type} de R$ {amount}")
        return self._make_request("POST", "/charges", charge_data)
    
    def obter_cobranca(self, charge_id: str) -> Dict:
        """Obtém detalhes de uma cobrança"""
        return self._make_request("GET", f"/charges/{charge_id}")
    
    def listar_cobrancas(self, filters: Dict = None) -> Dict:
        """Lista todas as cobrações"""
        logger.info("📋 Listando cobrações...")
        return self._make_request("GET", "/charges")
    
    def atualizar_cobranca(self, charge_id: str, data: Dict) -> Dict:
        """Atualiza uma cobrança"""
        return self._make_request("PUT", f"/charges/{charge_id}", data)
    
    def deletar_cobranca(self, charge_id: str) -> Dict:
        """Deleta uma cobrança"""
        return self._make_request("DELETE", f"/charges/{charge_id}")
    
    def restaurar_cobranca(self, charge_id: str) -> Dict:
        """Restaura uma cobrança deletada"""
        return self._make_request("POST", f"/charges/{charge_id}/restore", {})
    
    # ========== PAGAMENTOS ==========
    
    def confirmar_pagamento(self, charge_id: str) -> Dict:
        """Confirma um pagamento no Asaas"""
        logger.info(f"✅ Confirmando pagamento: {charge_id}")
        return self._make_request("POST", f"/charges/{charge_id}/confirm", {})
    
    def reembolsar_pagamento(self, charge_id: str) -> Dict:
        """Reembolsa um pagamento"""
        logger.info(f"💸 Reembolsando pagamento: {charge_id}")
        return self._make_request("POST", f"/charges/{charge_id}/refund", {})
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def obter_dados_pix(self, charge_id: str) -> Dict:
        """Extrai dados de PIX de uma cobrança"""
        charge = self.obter_cobranca(charge_id)
        
        if charge.get("error"):
            return charge
        
        return {
            "charge_id": charge_id,
            "qr_code": charge.get("pixQrCode", ""),
            "copy_paste": charge.get("pixCopyPaste", ""),
            "value": charge.get("value", 0),
            "status": charge.get("status", "PENDING"),
            "expiration": charge.get("pixExpiration", ""),
            "qr_code_url": charge.get("pixQrCodeUrl", "")
        }
    
    def obter_dados_boleto(self, charge_id: str) -> Dict:
        """Extrai dados de Boleto de uma cobrança"""
        charge = self.obter_cobranca(charge_id)
        
        if charge.get("error"):
            return charge
        
        return {
            "charge_id": charge_id,
            "barcode": charge.get("barCode", ""),
            "digitable_line": charge.get("bankSlip", ""),
            "invoice_url": charge.get("invoiceUrl", ""),
            "value": charge.get("value", 0),
            "due_date": charge.get("dueDate", ""),
            "status": charge.get("status", "PENDING")
        }
    
    def obter_dados_cartao(self, charge_id: str) -> Dict:
        """Extrai dados de Cartão de uma cobrança"""
        charge = self.obter_cobranca(charge_id)
        
        if charge.get("error"):
            return charge
        
        return {
            "charge_id": charge_id,
            "payment_url": charge.get("invoiceUrl", ""),
            "value": charge.get("value", 0),
            "status": charge.get("status", "PENDING")
        }
    
    # ========== UTILITÁRIOS ==========
    
    @staticmethod
    def _get_due_date(days: int = 30) -> str:
        """Retorna data de vencimento formatada"""
        return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    @staticmethod
    def _sanitize_cpf(cpf: str) -> str:
        """Remove caracteres especiais de CPF/CNPJ"""
        if not cpf:
            return "12345678901234"
        return ''.join(c for c in str(cpf) if c.isdigit())[:14]
    
    def testar_conexao(self) -> Dict:
        """Testa a conexão com a API Asaas"""
        logger.info("🧪 Testando conexão com Asaas...")
        result = self.listar_clientes()
        
        if result.get("error"):
            logger.error("❌ Erro ao conectar com Asaas")
            return {"success": False, "error": result}
        else:
            logger.info("✅ Conexão com Asaas OK")
            return {"success": True}


def criar_pagamento_completo(
    lead: Dict,
    valor: float,
    descricao: str = "Serviço Médico ON",
    asaas: AsaasIntegration = None
) -> Dict:
    """
    Cria um pagamento com todas as opções (PIX, Boleto, Cartão)
    
    Args:
        lead: Dicionário com dados do lead (name, email, cpf, ...)
        valor: Valor do pagamento
        descricao: Descrição da cobrança
        asaas: Instância de AsaasIntegration (cria nova se não fornecida)
        
    Returns:
        Dicionário com opções de pagamento
    """
    if not asaas:
        asaas = AsaasIntegration()
    
    logger.info(f"💳 Criando pagamento completo para {lead.get('name')} - R$ {valor}")
    
    # Criar cliente
    customer_result = asaas.criar_cliente(
        name=lead.get("name", "Cliente"),
        email=lead.get("email", "noreply@onmedicina.com"),
        cpf_cnpj=lead.get("cpf", "12345678901234"),
        phone=lead.get("phone", ""),
        city=lead.get("city", ""),
        state=lead.get("state", "")
    )
    
    if customer_result.get("error"):
        return {
            "error": True,
            "message": f"Erro ao criar cliente: {customer_result.get('message')}"
        }
    
    customer_id = customer_result.get("id")
    payment_options = {}
    
    # Criar cobrança PIX
    try:
        pix_charge = asaas.criar_cobranca(
            customer_id=customer_id,
            amount=valor,
            description=descricao,
            billing_type="PIX"
        )
        
        if not pix_charge.get("error"):
            pix_data = asaas.obter_dados_pix(pix_charge.get("id"))
            payment_options["pix"] = pix_data
            logger.info(f"✅ Cobrança PIX criada: {pix_charge.get('id')}")
    except Exception as e:
        logger.error(f"❌ Erro ao criar cobrança PIX: {str(e)}")
    
    # Criar cobrança Boleto
    try:
        boleto_charge = asaas.criar_cobranca(
            customer_id=customer_id,
            amount=valor,
            description=descricao,
            billing_type="BOLETO"
        )
        
        if not boleto_charge.get("error"):
            boleto_data = asaas.obter_dados_boleto(boleto_charge.get("id"))
            payment_options["boleto"] = boleto_data
            logger.info(f"✅ Cobrança Boleto criada: {boleto_charge.get('id')}")
    except Exception as e:
        logger.error(f"❌ Erro ao criar cobrança Boleto: {str(e)}")
    
    # Criar cobrança Cartão
    try:
        card_charge = asaas.criar_cobranca(
            customer_id=customer_id,
            amount=valor,
            description=descricao,
            billing_type="CREDIT_CARD"
        )
        
        if not card_charge.get("error"):
            card_data = asaas.obter_dados_cartao(card_charge.get("id"))
            payment_options["credit_card"] = card_data
            logger.info(f"✅ Cobrança Cartão criada: {card_charge.get('id')}")
    except Exception as e:
        logger.error(f"❌ Erro ao criar cobrança Cartão: {str(e)}")
    
    return {
        "success": True,
        "customer_id": customer_id,
        "payment_options": payment_options,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("✅ Asaas Integration V2 carregado com sucesso!")
    print("\n📚 Disponível:")
    print("   - AsaasIntegration: Classe principal")
    print("   - criar_pagamento_completo(): Função para criar pagamentos")
    print("\n🧪 Para testar, execute:")
    print("""
    asaas = AsaasIntegration()
    
    # Testar conexão
    resultado = asaas.testar_conexao()
    print(resultado)
    
    # Criar pagamento
    pagamento = criar_pagamento_completo(
        lead={
            'name': 'João Silva',
            'email': 'joao@example.com',
            'cpf': '12345678901234'
        },
        valor=100.00
    )
    print(pagamento)
    """)
