"""
Integração com API Asaas - Pagamentos PIX, Boleto, Cartão de Crédito
Documentação: https://docs.asaas.com/
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class AsaasIntegration:
    """Classe para integração com API Asaas"""
    
    # Configurações da API
    API_KEY = "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmNiOGQ2OWQ0LTRkNGMtNDhiYi04M2Q4LTJiZTRmNDk0MDgxMDo6JGFhY2hfYTVhY2NmY2QtNzBlMS00N2FlLWI2YjYtYjFiMzFlN2UyNTNh"
    API_BASE_URL = "https://api.asaas.com/v3"
    SANDBOX_URL = "https://sandbox.asaas.com/api/v3"
    
    # CPF padrão da conta (precisa ser configurado)
    CPFCNPJ = "12345678901234"  # CPF/CNPJ que deve ser configurado nas variáveis de ambiente
    
    def __init__(self, api_key: str = None, sandbox: bool = False):
        """
        Inicializa a integração com Asaas
        
        Args:
            api_key: Chave da API Asaas
            sandbox: Se True, usa ambiente de teste
        """
        self.api_key = api_key or self.API_KEY
        self.base_url = self.SANDBOX_URL if sandbox else self.API_BASE_URL
        self.sandbox = sandbox
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "access_token": self.api_key
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """
        Realiza uma requisição na API Asaas
        
        Args:
            method: GET, POST, PUT, DELETE
            endpoint: Endpoint da API (ex: /charges)
            data: Dados para POST/PUT
            
        Returns:
            Resposta da API em formato JSON
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Método HTTP {method} não suportado")
            
            logger.info(f"{method} {url} - Status: {response.status_code}")
            
            if response.status_code >= 400:
                logger.error(f"Erro na API Asaas: {response.text}")
                return {"error": True, "status_code": response.status_code, "message": response.text}
            
            return response.json() if response.text else {"success": True}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return {"error": True, "message": str(e)}
    
    def criar_cobranca(
        self,
        customer_id: str = None,
        name: str = None,
        email: str = None,
        cpf_cnpj: str = None,
        amount: float = 0.0,
        description: str = None,
        due_date: str = None,
        billing_type: str = "PIX"  # PIX, BOLETO, CREDIT_CARD
    ) -> Dict:
        """
        Cria uma cobrança (charge) no Asaas
        
        Args:
            customer_id: ID do cliente (se já existe)
            name: Nome do cliente
            email: Email do cliente
            cpf_cnpj: CPF/CNPJ do cliente
            amount: Valor da cobrança
            description: Descrição da cobrança
            due_date: Data de vencimento (YYYY-MM-DD)
            billing_type: PIX, BOLETO, CREDIT_CARD
            
        Returns:
            Dados da cobrança criada
        """
        if not customer_id:
            # Criar cliente se não existir
            customer = self.criar_cliente(name, email, cpf_cnpj)
            if customer.get("error"):
                return customer
            customer_id = customer.get("id")
        
        # Data de vencimento padrão (amanhã)
        if not due_date:
            due_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        data = {
            "customerId": customer_id,
            "billingType": billing_type,
            "value": amount,
            "description": description or f"Pagamento - {datetime.now().strftime('%d/%m/%Y')}",
            "dueDate": due_date,
            "remoteId": f"lead_{customer_id}_{datetime.now().timestamp()}"
        }
        
        if billing_type == "PIX":
            data["pixAddressKey"] = None  # PIX aleatório
        
        response = self._make_request("POST", "/charges", data)
        
        if not response.get("error"):
            logger.info(f"Cobrança criada: {response.get('id')}")
            return {
                "success": True,
                "charge_id": response.get("id"),
                "status": response.get("status"),
                "invoice_url": response.get("invoiceUrl"),
                "pix_qr_code": response.get("pixQrCode"),
                "pix_copy_paste": response.get("pixCopyPaste"),
                "boleto_barcode": response.get("barcode"),
                "boleto_digitable_line": response.get("digitableLine"),
                "payment_url": response.get("invoiceUrl"),
                "raw_response": response
            }
        
        return response
    
    def criar_cliente(self, name: str, email: str, cpf_cnpj: str = None) -> Dict:
        """
        Cria um cliente no Asaas
        
        Args:
            name: Nome completo
            email: Email
            cpf_cnpj: CPF ou CNPJ
            
        Returns:
            Dados do cliente criado
        """
        if not cpf_cnpj:
            cpf_cnpj = self.CPFCNPJ
        
        data = {
            "name": name,
            "email": email,
            "cpfCnpj": cpf_cnpj,
            "personType": "INDIVIDUAL",
            "notificationDisabled": False
        }
        
        response = self._make_request("POST", "/customers", data)
        
        if not response.get("error"):
            logger.info(f"Cliente criado: {response.get('id')}")
            return {
                "success": True,
                "customer_id": response.get("id"),
                "raw_response": response
            }
        
        return response
    
    def obter_cobranca(self, charge_id: str) -> Dict:
        """
        Obtém detalhes de uma cobrança
        
        Args:
            charge_id: ID da cobrança
            
        Returns:
            Dados da cobrança
        """
        response = self._make_request("GET", f"/charges/{charge_id}")
        
        if not response.get("error"):
            return {
                "success": True,
                "charge_id": response.get("id"),
                "status": response.get("status"),
                "value": response.get("value"),
                "due_date": response.get("dueDate"),
                "confirmed_date": response.get("confirmedDate"),
                "pix_qr_code": response.get("pixQrCode"),
                "boleto_barcode": response.get("barcode"),
                "raw_response": response
            }
        
        return response
    
    def gerar_pix_qrcode(self, charge_id: str) -> Dict:
        """
        Gera QR Code PIX para uma cobrança
        
        Args:
            charge_id: ID da cobrança
            
        Returns:
            Dados do QR Code
        """
        charge = self.obter_cobranca(charge_id)
        
        if charge.get("success"):
            return {
                "success": True,
                "pix_qr_code": charge.get("pix_qr_code"),
                "pix_copy_paste": charge.get("raw_response", {}).get("pixCopyPaste"),
                "amount": charge.get("value")
            }
        
        return charge
    
    def gerar_boleto_pdf(self, charge_id: str) -> Dict:
        """
        Obtém link para PDF do boleto
        
        Args:
            charge_id: ID da cobrança
            
        Returns:
            URL do PDF
        """
        charge = self.obter_cobranca(charge_id)
        
        if charge.get("success"):
            return {
                "success": True,
                "boleto_barcode": charge.get("boleto_barcode"),
                "boleto_digitable_line": charge.get("raw_response", {}).get("digitableLine"),
                "pdf_url": charge.get("raw_response", {}).get("invoiceUrl"),
                "amount": charge.get("value")
            }
        
        return charge
    
    def listar_cobancas(self, customer_id: str = None, limit: int = 100) -> Dict:
        """
        Lista cobranças
        
        Args:
            customer_id: Filtrar por cliente
            limit: Quantidade máxima de resultados
            
        Returns:
            Lista de cobranças
        """
        endpoint = f"/charges?limit={limit}"
        if customer_id:
            endpoint += f"&customerId={customer_id}"
        
        response = self._make_request("GET", endpoint)
        
        if not response.get("error"):
            return {
                "success": True,
                "charges": response.get("data", []),
                "total": response.get("totalCount", 0)
            }
        
        return response
    
    def confirmar_pagamento(self, charge_id: str) -> Dict:
        """
        Confirma um pagamento (após webhook)
        
        Args:
            charge_id: ID da cobrança
            
        Returns:
            Status da confirmação
        """
        charge = self.obter_cobranca(charge_id)
        
        if charge.get("success"):
            status = charge.get("raw_response", {}).get("status")
            
            return {
                "success": True,
                "charge_id": charge_id,
                "payment_confirmed": status in ["CONFIRMED", "RECEIVED"],
                "status": status
            }
        
        return charge
    
    def listar_clientes(self, limit: int = 100) -> Dict:
        """
        Lista clientes cadastrados
        
        Args:
            limit: Quantidade máxima de resultados
            
        Returns:
            Lista de clientes
        """
        response = self._make_request("GET", f"/customers?limit={limit}")
        
        if not response.get("error"):
            return {
                "success": True,
                "customers": response.get("data", []),
                "total": response.get("totalCount", 0)
            }
        
        return response


def criar_link_pagamento_completo(lead_data: Dict, amount: float = 0.0) -> Dict:
    """
    Função auxiliar para criar um link de pagamento completo
    Suporta PIX, Boleto e Cartão de Crédito
    
    Args:
        lead_data: Dados do lead {'id', 'name', 'email', 'cpf_cnpj'}
        amount: Valor do pagamento
        
    Returns:
        Dados de pagamento com opções (PIX, Boleto, Cartão)
    """
    asaas = AsaasIntegration()
    
    result = {
        "lead_id": lead_data.get("id"),
        "lead_name": lead_data.get("name"),
        "amount": amount,
        "payment_options": {}
    }
    
    # Criar cobrança para PIX
    pix_charge = asaas.criar_cobranca(
        name=lead_data.get("name"),
        email=lead_data.get("email"),
        cpf_cnpj=lead_data.get("cpf_cnpj"),
        amount=amount,
        description=f"Pagamento - {lead_data.get('name')}",
        billing_type="PIX"
    )
    
    if pix_charge.get("success"):
        result["payment_options"]["pix"] = {
            "charge_id": pix_charge.get("charge_id"),
            "qr_code": pix_charge.get("pix_qr_code"),
            "copy_paste": pix_charge.get("pix_copy_paste"),
            "status": "pending"
        }
    
    # Criar cobrança para Boleto
    boleto_charge = asaas.criar_cobranca(
        name=lead_data.get("name"),
        email=lead_data.get("email"),
        cpf_cnpj=lead_data.get("cpf_cnpj"),
        amount=amount,
        description=f"Pagamento - {lead_data.get('name')}",
        billing_type="BOLETO"
    )
    
    if boleto_charge.get("success"):
        result["payment_options"]["boleto"] = {
            "charge_id": boleto_charge.get("charge_id"),
            "barcode": boleto_charge.get("boleto_barcode"),
            "digitable_line": boleto_charge.get("boleto_digitable_line"),
            "invoice_url": boleto_charge.get("payment_url"),
            "status": "pending"
        }
    
    # Criar cobrança para Cartão (será redirecionado)
    card_charge = asaas.criar_cobranca(
        name=lead_data.get("name"),
        email=lead_data.get("email"),
        cpf_cnpj=lead_data.get("cpf_cnpj"),
        amount=amount,
        description=f"Pagamento - {lead_data.get('name')}",
        billing_type="CREDIT_CARD"
    )
    
    if card_charge.get("success"):
        result["payment_options"]["credit_card"] = {
            "charge_id": card_charge.get("charge_id"),
            "payment_url": card_charge.get("payment_url"),
            "status": "pending"
        }
    
    result["webhook_url"] = "https://app.onmedicinainternacional.com/comercial/webhook-setup"
    
    return result


if __name__ == "__main__":
    # Teste de integração
    asaas = AsaasIntegration(sandbox=True)
    
    # Criar cliente
    cliente = asaas.criar_cliente("João Silva", "joao@example.com", "12345678901234")
    print("Cliente criado:", cliente)
    
    # Criar cobrança
    if cliente.get("success"):
        cobranca = asaas.criar_cobranca(
            customer_id=cliente.get("customer_id"),
            amount=100.00,
            description="Teste de integração"
        )
        print("Cobrança criada:", cobranca)
