"""
IntegraICP Service — Assinatura Digital ICP-Brasil
Integração com a plataforma IntegraICP (https://integraicp.com.br)
Suporta: Vidaas (Valid), BirdID (Soluti) e outros PSCs

Fluxo:
1. generate_pkce_pair() → secret_data (challenge) + code_verifier
2. get_clearances()     → lista de provedores (Vidaas, BirdID, etc.)
3. Usuário autentica no provedor → callback com credential_id
4. get_credential()     → informações do certificado
5. sign_documents()     → assinatura digital SHA256
"""

import os
import hashlib
import base64
import secrets
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

INTEGRAICP_BASE_URL = "https://services.integraicp.com.br"


class IntegraICPService:
    """Serviço de integração com IntegraICP para assinatura digital ICP-Brasil."""

    def __init__(self, channel_id: str = None, callback_base_url: str = None):
        self.channel_id = channel_id or os.environ.get('INTEGRAICP_CHANNEL_ID', '')
        self.callback_base_url = callback_base_url or os.environ.get(
            'INTEGRAICP_CALLBACK_URL',
            'https://app.onmedicinainternacional.com'
        )
        if not self.channel_id:
            logger.warning("⚠️ INTEGRAICP_CHANNEL_ID não configurado no .env")

    # ─── RFC 7636 PKCE ──────────────────────────────────────────────
    @staticmethod
    def generate_pkce_pair() -> Dict[str, str]:
        """
        Gera par PKCE (RFC 7636) para autenticação segura.
        Returns:
            {
                'code_verifier': str,    → usado em /credentials e /signatures
                'code_challenge': str    → usado em /authentications (secret_data)
            }
        """
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
        code_verifier = ''.join(secrets.choice(chars) for _ in range(43))

        # S256: BASE64URL( SHA256( code_verifier ) )
        digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
        code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode('ascii')

        return {
            'code_verifier': code_verifier,
            'code_challenge': code_challenge
        }

    # ─── 1. Authentications — Listar Clearances ─────────────────────
    def get_authentications_url(
        self,
        code_challenge: str,
        callback_uri: str,
        subject_key: str = None,
        credential_lifetime: int = 3600,
        autostart: bool = False
    ) -> str:
        """
        Monta a URL para GET /authentications.
        O frontend deve fazer redirect ou fetch para esta URL.
        """
        url = (
            f"{INTEGRAICP_BASE_URL}/c/{self.channel_id}/icp/v3/authentications"
            f"?secret_data={code_challenge}"
            f"&secret_type=code_challenge"
            f"&callback_uri={callback_uri}"
            f"&credential_lifetime={credential_lifetime}"
        )
        if subject_key:
            url += f"&subject_key={subject_key}&subject_type=CPF"
        if autostart:
            url += "&autostart=true"
        return url

    def build_callback_uri(self, doc_type: str, doc_id: str, session_id: str) -> str:
        """Monta a URI de callback com parâmetros opacos."""
        return (
            f"{self.callback_base_url}/api/assinatura/callback"
            f"?doc_type={doc_type}&doc_id={doc_id}&session_id={session_id}"
        )

    # ─── 2. Credentials — Obter dados do certificado ────────────────
    def get_credentials_url(self, credential_id: str, code_verifier: str) -> str:
        """
        Monta a URL para GET /credentials/{credentialId}.
        Chamado após receber credentialId via callback.
        """
        return (
            f"{INTEGRAICP_BASE_URL}/c/{self.channel_id}/icp/v3/credentials/{credential_id}"
            f"?secret_data={code_verifier}&secret_type=code_verifier"
        )

    # ─── 3. Signatures — Assinar documentos ─────────────────────────
    def get_signatures_url(self) -> str:
        """URL base para POST /signatures."""
        return f"{INTEGRAICP_BASE_URL}/c/{self.channel_id}/icp/v3/signatures"

    def build_signature_request(
        self,
        credential_id: str,
        code_verifier: str,
        documents: List[Dict],
        signature_policy: str = "CMS"
    ) -> Dict:
        """
        Monta o payload para POST /signatures.
        Args:
            credential_id: ID recebido após autenticação
            code_verifier: Código verificador PKCE original
            documents: Lista de { content_id, content_bytes_or_hash, description }
            signature_policy: "RAW" ou "CMS" (padrão CMS)
        Returns:
            JSON request body para a API de assinaturas
        """
        requests_list = []
        for doc in documents:
            if 'content_digest' in doc:
                digest_b64 = doc['content_digest']
            elif 'content_bytes' in doc:
                sha = hashlib.sha256(doc['content_bytes']).digest()
                digest_b64 = base64.b64encode(sha).decode('ascii')
            elif 'content_hash_hex' in doc:
                sha_bytes = bytes.fromhex(doc['content_hash_hex'])
                digest_b64 = base64.b64encode(sha_bytes).decode('ascii')
            else:
                raise ValueError(f"Documento sem hash: {doc.get('content_id', '?')}")

            requests_list.append({
                "contentId": doc.get('content_id', f"doc_{len(requests_list)+1}"),
                "contentDigest": digest_b64,
                "contentDescription": doc.get('description', 'Documento médico'),
                "signaturePolicy": signature_policy
            })

        return {
            "credentialId": credential_id,
            "secretType": "code_verifier",
            "secretData": code_verifier,
            "requests": requests_list
        }

    # ─── Helpers ─────────────────────────────────────────────────────
    @staticmethod
    def calculate_sha256_b64(content: bytes) -> str:
        """Calcula SHA256 e codifica em Base64 (padrão IntegraICP)."""
        sha = hashlib.sha256(content).digest()
        return base64.b64encode(sha).decode('ascii')

    @staticmethod
    def calculate_sha256_hex(content: str) -> str:
        """Calcula SHA256 hexadecimal de uma string."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado."""
        return bool(self.channel_id)
