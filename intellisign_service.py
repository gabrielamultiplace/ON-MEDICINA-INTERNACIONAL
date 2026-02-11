"""
Intellisign Service — Assinatura Eletrônica de Documentos para Pacientes
Integração com a plataforma Intellisign da Soluti (https://assine.online)

Fluxo para envio de documentos para assinatura do paciente:
1. Autenticar via OAuth2 (client_credentials) → access_token
2. Upload do PDF → item_id
3. Criar envelope (draft) → envelope_id
4. Adicionar documento ao envelope (usando item_id)
5. Adicionar destinatário (paciente com email/telefone)
6. Enviar envelope → paciente recebe link por email
7. Paciente assina via link
8. Consultar status / Download do documento assinado
"""

import os
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

INTELLISIGN_BASE_URL = "https://api.intellisign.com"

try:
    import requests as http_client
except ImportError:
    http_client = None
    logger.warning("⚠️ Módulo 'requests' não disponível — Intellisign desabilitado")


class IntellisignService:
    """Serviço de integração com Intellisign para assinatura eletrônica de documentos."""

    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id or os.environ.get('INTELLISIGN_CLIENT_ID', '')
        self.client_secret = client_secret or os.environ.get('INTELLISIGN_CLIENT_SECRET', '')
        self._access_token = None
        self._token_expires_at = 0

        if not self.client_id:
            logger.warning("⚠️ INTELLISIGN_CLIENT_ID não configurado no .env")

    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado."""
        return bool(self.client_id and self.client_secret)

    # ─── OAuth2 Token Management ─────────────────────────────────────
    def _get_token(self) -> str:
        """Obtém ou renova access_token via client_credentials."""
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        if not http_client:
            raise RuntimeError("Módulo 'requests' não disponível")

        url = f"{INTELLISIGN_BASE_URL}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "*"
        }

        logger.info("Intellisign: obtendo access_token...")
        resp = http_client.post(url, json=payload, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            self._access_token = data.get('access_token', '')
            expires_in = data.get('expires_in', 3600)
            self._token_expires_at = time.time() + expires_in
            logger.info(f"Intellisign: token obtido, expira em {expires_in}s")
            return self._access_token

        logger.error(f"Intellisign: erro ao obter token — {resp.status_code}: {resp.text}")
        raise RuntimeError(f"Falha na autenticação Intellisign: {resp.status_code}")

    def _headers(self, org_id: str = None) -> Dict:
        """Headers de autenticação para chamadas à API."""
        token = self._get_token()
        h = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if org_id:
            h['X-Organization'] = org_id
        return h

    # ─── Perfil ──────────────────────────────────────────────────────
    def get_profile(self) -> Dict:
        """Retorna informações do perfil da conta."""
        resp = http_client.get(
            f"{INTELLISIGN_BASE_URL}/v1/me",
            headers=self._headers(),
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text, 'status_code': resp.status_code}

    # ─── Upload de Arquivo ───────────────────────────────────────────
    def upload_file(self, file_path: str, parent_id: str = None) -> Dict:
        """
        Faz upload de um arquivo PDF para o armazenamento Intellisign.
        Retorna o item com id para uso no envelope.
        """
        token = self._get_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

        data = {}
        if parent_id:
            data['parent'] = parent_id

        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
            resp = http_client.post(
                f"{INTELLISIGN_BASE_URL}/v1/items/upload",
                headers=headers,
                data=data,
                files=files,
                timeout=60
            )

        if resp.status_code in (200, 201):
            result = resp.json()
            logger.info(f"Intellisign: arquivo uploaded — id={result.get('id')}")
            return result

        logger.error(f"Intellisign: erro upload — {resp.status_code}: {resp.text}")
        return {'error': resp.text, 'status_code': resp.status_code}

    def upload_file_bytes(self, content: bytes, filename: str, parent_id: str = None) -> Dict:
        """
        Faz upload de bytes de PDF direto (sem salvar em disco).
        """
        token = self._get_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }

        data = {}
        if parent_id:
            data['parent'] = parent_id

        files = {'file': (filename, content, 'application/pdf')}
        resp = http_client.post(
            f"{INTELLISIGN_BASE_URL}/v1/items/upload",
            headers=headers,
            data=data,
            files=files,
            timeout=60
        )

        if resp.status_code in (200, 201):
            result = resp.json()
            logger.info(f"Intellisign: arquivo uploaded (bytes) — id={result.get('id')}")
            return result

        logger.error(f"Intellisign: erro upload bytes — {resp.status_code}: {resp.text}")
        return {'error': resp.text, 'status_code': resp.status_code}

    # ─── Envelopes ───────────────────────────────────────────────────
    def create_envelope(
        self,
        subject: str = None,
        message: str = None,
        title: str = None,
        expire_at: str = None,
        reminder_hours: int = 72,
        triggers: list = None
    ) -> Dict:
        """
        Cria um envelope em modo draft.
        """
        payload = {}
        if subject:
            payload['subject'] = subject
        if message:
            payload['message'] = message
        if title:
            payload['title'] = title
        if expire_at:
            payload['expire_at'] = expire_at
        if reminder_hours:
            payload['action_reminder_frequency'] = reminder_hours
        if triggers:
            payload['triggers'] = triggers

        resp = http_client.post(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes",
            headers=self._headers(),
            json=payload,
            timeout=30
        )

        if resp.status_code in (200, 201):
            result = resp.json()
            logger.info(f"Intellisign: envelope criado — id={result.get('id')}")
            return result

        logger.error(f"Intellisign: erro ao criar envelope — {resp.status_code}: {resp.text}")
        return {'error': resp.text, 'status_code': resp.status_code}

    def add_document_to_envelope(self, envelope_id: str, file_item_id: str) -> Dict:
        """
        Adiciona um documento (já uploaded) ao envelope.
        """
        payload = {"file": file_item_id}
        resp = http_client.post(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}/documents",
            headers=self._headers(),
            json=payload,
            timeout=30
        )

        if resp.status_code in (200, 201):
            result = resp.json()
            logger.info(f"Intellisign: doc adicionado ao envelope — doc_id={result.get('id')}")
            return result

        logger.error(f"Intellisign: erro ao adicionar doc — {resp.status_code}: {resp.text}")
        return {'error': resp.text, 'status_code': resp.status_code}

    def add_recipient(
        self,
        envelope_id: str,
        name: str,
        email: str = None,
        phone: str = None,
        recipient_type: str = 'signer',
        signature_type: str = 'simple',
        routing_order: int = None
    ) -> Dict:
        """
        Adiciona um destinatário ao envelope.
        - type: signer, approver, carbon-copy
        - signature_type: simple (eletrônica) ou qualified (ICP-Brasil)
        """
        addressee = {}
        if email:
            addressee['email'] = email
            addressee['via'] = 'email'
        elif phone:
            addressee['phone'] = phone
            addressee['via'] = 'sms'

        if name:
            addressee['name'] = name

        payload = {
            "type": recipient_type,
            "signature_type": signature_type,
            "addressees": [addressee]
        }
        if routing_order is not None:
            payload['routing_order'] = routing_order

        resp = http_client.post(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}/recipients",
            headers=self._headers(),
            json=payload,
            timeout=30
        )

        if resp.status_code in (200, 201):
            result = resp.json()
            logger.info(f"Intellisign: destinatário adicionado — id={result.get('id')}")
            return result

        logger.error(f"Intellisign: erro add recipient — {resp.status_code}: {resp.text}")
        return {'error': resp.text, 'status_code': resp.status_code}

    def add_signature_field(
        self,
        envelope_id: str,
        document_id: str,
        recipient_id: str,
        page: int = 1,
        x: int = 350,
        y: int = 50,
        width: int = 200,
        height: int = 60
    ) -> Dict:
        """
        Adiciona campo de assinatura ao documento PDF.
        """
        payload = {
            "recipient": recipient_id,
            "is_required": True,
            "type": "signature",
            "name": "assinatura_paciente",
            "title": "Assinatura do Paciente",
            "widgets": [{
                "page": page,
                "x_axis": x,
                "y_axis": y,
                "width": width,
                "height": height
            }]
        }

        resp = http_client.post(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}/documents/{document_id}/fields",
            headers=self._headers(),
            json=payload,
            timeout=30
        )

        if resp.status_code in (200, 201):
            result = resp.json()
            logger.info(f"Intellisign: campo assinatura adicionado — id={result.get('id')}")
            return result

        logger.error(f"Intellisign: erro add field — {resp.status_code}: {resp.text}")
        return {'error': resp.text, 'status_code': resp.status_code}

    def send_envelope(self, envelope_id: str) -> Dict:
        """
        Envia o envelope para os destinatários.
        O paciente receberá notificação por email/SMS com link para assinar.
        """
        resp = http_client.post(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}/send",
            headers=self._headers(),
            timeout=30
        )

        if resp.status_code in (200, 202):
            result = resp.json()
            logger.info(f"Intellisign: envelope enviado — {envelope_id}")
            return result

        logger.error(f"Intellisign: erro ao enviar — {resp.status_code}: {resp.text}")
        return {'error': resp.text, 'status_code': resp.status_code}

    def get_envelope(self, envelope_id: str, extended: bool = True) -> Dict:
        """
        Consulta o status de um envelope.
        Com extended=True retorna documentos, destinatários e link de download.
        """
        params = {'extended': 'true'} if extended else {}
        resp = http_client.get(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}",
            headers=self._headers(),
            params=params,
            timeout=15
        )

        if resp.status_code == 200:
            return resp.json()

        logger.error(f"Intellisign: erro get envelope — {resp.status_code}: {resp.text}")
        return {'error': resp.text, 'status_code': resp.status_code}

    def list_envelopes(self, state: str = None, page: int = 1, limit: int = 20) -> Dict:
        """Lista envelopes enviados."""
        params = {'page': page, 'limit': limit, 'include': 'recipients_stats'}
        if state:
            params['filter[state]'] = state

        resp = http_client.get(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes",
            headers=self._headers(),
            params=params,
            timeout=15
        )

        if resp.status_code == 200:
            return resp.json()

        return {'error': resp.text, 'status_code': resp.status_code}

    def cancel_envelope(self, envelope_id: str) -> Dict:
        """Cancela um envelope pendente."""
        resp = http_client.post(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}/cancel",
            headers=self._headers(),
            timeout=15
        )

        if resp.status_code in (200, 202):
            logger.info(f"Intellisign: envelope cancelado — {envelope_id}")
            return {'success': True}

        return {'error': resp.text, 'status_code': resp.status_code}

    def renotify_envelope(self, envelope_id: str) -> Dict:
        """Reenvia notificações ao destinatário."""
        resp = http_client.post(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}/renotify",
            headers=self._headers(),
            timeout=15
        )

        if resp.status_code in (200, 202):
            logger.info(f"Intellisign: renotificação enviada — {envelope_id}")
            return {'success': True}

        return {'error': resp.text, 'status_code': resp.status_code}

    def download_envelope(self, envelope_id: str) -> bytes:
        """Faz download do envelope assinado (ZIP com PDFs)."""
        resp = http_client.get(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}/download",
            headers={
                'Authorization': f'Bearer {self._get_token()}'
            },
            timeout=60
        )

        if resp.status_code == 200:
            return resp.content

        logger.error(f"Intellisign: erro download — {resp.status_code}")
        return None

    def get_recipients(self, envelope_id: str) -> Dict:
        """Lista destinatários de um envelope."""
        resp = http_client.get(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}/recipients",
            headers=self._headers(),
            timeout=15
        )

        if resp.status_code == 200:
            return resp.json()

        return {'error': resp.text, 'status_code': resp.status_code}

    def notify_recipient(self, envelope_id: str, recipient_id: str) -> Dict:
        """Envia notificação específica para um destinatário."""
        resp = http_client.post(
            f"{INTELLISIGN_BASE_URL}/v1/envelopes/{envelope_id}/recipients/{recipient_id}/notify",
            headers=self._headers(),
            timeout=15
        )

        if resp.status_code in (200, 202):
            return {'success': True}

        return {'error': resp.text, 'status_code': resp.status_code}

    # ─── Fluxo Completo ─────────────────────────────────────────────
    def enviar_para_assinatura(
        self,
        pdf_bytes: bytes,
        filename: str,
        paciente_nome: str,
        paciente_email: str = None,
        paciente_telefone: str = None,
        assunto: str = None,
        mensagem: str = None,
        titulo: str = None,
        expire_days: int = 30,
        signature_type: str = 'simple'
    ) -> Dict:
        """
        Fluxo completo: upload PDF → criar envelope → add doc → add recipient → enviar.
        
        Retorna dict com envelope_id, status, e detalhes.
        """
        if not self.is_configured():
            return {'error': 'Intellisign não configurado', 'status_code': 500}

        if not paciente_email and not paciente_telefone:
            return {'error': 'Email ou telefone do paciente é obrigatório', 'status_code': 400}

        try:
            # 1. Upload PDF
            upload_result = self.upload_file_bytes(pdf_bytes, filename)
            if 'error' in upload_result:
                return {'error': f'Erro no upload: {upload_result.get("error")}', 'step': 'upload'}

            file_item_id = upload_result.get('id')

            # 2. Criar envelope
            from datetime import timedelta
            expire_at = (datetime.now(timezone.utc) + timedelta(days=expire_days)).isoformat()

            envelope_result = self.create_envelope(
                subject=assunto or f'Documento para assinatura — {paciente_nome}',
                message=mensagem or f'Olá {paciente_nome}, por favor assine o documento anexo.',
                title=titulo or filename.replace('.pdf', ''),
                expire_at=expire_at,
                reminder_hours=72
            )
            if 'error' in envelope_result:
                return {'error': f'Erro ao criar envelope: {envelope_result.get("error")}', 'step': 'envelope'}

            envelope_id = envelope_result.get('id')

            # 3. Adicionar documento ao envelope
            doc_result = self.add_document_to_envelope(envelope_id, file_item_id)
            if 'error' in doc_result:
                return {'error': f'Erro ao adicionar documento: {doc_result.get("error")}', 'step': 'document'}

            document_id = doc_result.get('id')

            # 4. Adicionar destinatário (paciente)
            recipient_result = self.add_recipient(
                envelope_id=envelope_id,
                name=paciente_nome,
                email=paciente_email,
                phone=paciente_telefone,
                recipient_type='signer',
                signature_type=signature_type
            )
            if 'error' in recipient_result:
                return {'error': f'Erro ao adicionar destinatário: {recipient_result.get("error")}', 'step': 'recipient'}

            recipient_id = recipient_result.get('id')

            # 5. Adicionar campo de assinatura no PDF
            if document_id and recipient_id:
                self.add_signature_field(
                    envelope_id=envelope_id,
                    document_id=document_id,
                    recipient_id=recipient_id,
                    page=1,
                    x=350,
                    y=50,
                    width=200,
                    height=60
                )

            # 6. Enviar envelope
            send_result = self.send_envelope(envelope_id)
            if 'error' in send_result:
                return {'error': f'Erro ao enviar: {send_result.get("error")}', 'step': 'send'}

            logger.info(f"✅ Intellisign: documento enviado para {paciente_nome} ({paciente_email or paciente_telefone})")

            return {
                'success': True,
                'envelope_id': envelope_id,
                'hashid': envelope_result.get('hashid', ''),
                'file_item_id': file_item_id,
                'document_id': document_id,
                'recipient_id': recipient_id,
                'action_token': send_result.get('action_token', ''),
                'status': 'in-transit',
                'enviado_para': paciente_email or paciente_telefone,
                'enviado_em': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Intellisign erro no fluxo completo: {e}")
            return {'error': str(e), 'step': 'exception'}
