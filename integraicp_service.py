"""
IntegraICP Service — Assinatura Digital ICP-Brasil
Integração com a plataforma IntegraICP (https://integraicp.com.br)
Suporta: Vidaas (Valid), BirdID (Soluti) e outros PSCs

Fluxo conforme diagrama de sequência oficial:
1. generate_pkce_pair()      → code_challenge (para /authentications) + code_verifier (para /credentials e /signatures)
2. get_clearances()          → GET /authentications → lista de Clearances (provedores)
3. Usuário seleciona provider → GET clearanceEndpoint → HTTP 302 → autenticação no provedor
4. Provedor notifica IntegraICP → IntegraICP envia CredentialId para callback_uri (?code={CredentialId})
5. get_credential()          → GET /credentials/{credentialId}?secret_data={code_verifier} → dados do certificado
6. sign_documents()          → POST /signatures com credentialId + code_verifier + SHA256 hashes → assinaturas
"""

import os
import hashlib
import base64
import secrets
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

INTEGRAICP_BASE_URL = "https://services.integraicp.com.br"

# Importar requests para chamadas server-side
try:
    import requests as http_client
except ImportError:
    http_client = None
    logger.warning("⚠️ Módulo 'requests' não disponível — chamadas HTTP à IntegraICP desabilitadas")


class IntegraICPService:
    """Serviço de integração server-side com IntegraICP para assinatura digital ICP-Brasil."""

    def __init__(self, channel_id: str = None, callback_base_url: str = None):
        self.channel_id = channel_id or os.environ.get('INTEGRAICP_CHANNEL_ID', '')
        self.callback_base_url = callback_base_url or os.environ.get(
            'INTEGRAICP_CALLBACK_URL',
            'https://app.onmedicinainternacional.com'
        )
        if not self.channel_id:
            logger.warning("⚠️ INTEGRAICP_CHANNEL_ID não configurado no .env")

    # ─── RFC 7636 PKCE (conforme documentação IntegraICP) ────────────
    @staticmethod
    def generate_pkce_pair() -> Dict[str, str]:
        """
        Gera par PKCE (RFC 7636) para autenticação segura.
        - code_verifier: string aleatória de 43 chars → usado em /credentials e /signatures (secret_data)
        - code_challenge: BASE64URL(SHA256(code_verifier)) → usado em /authentications (secret_data)
        
        Conforme exemplo NodeJS da documentação IntegraICP.
        """
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
        code_verifier = ''.join(secrets.choice(chars) for _ in range(43))

        # S256: BASE64URL( SHA256( code_verifier ) ) — sem padding '='
        digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
        code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode('ascii')

        return {
            'code_verifier': code_verifier,      # secretDataForSignaturesAndCredentials
            'code_challenge': code_challenge      # secretDataForAuthentications
        }

    # ─── 1. GET /authentications — Listar Clearances ─────────────────
    def get_clearances(
        self,
        code_challenge: str,
        callback_uri: str,
        subject_key: str = None,
        credential_lifetime: int = 3600,
        clearance_lifetime: int = 86400,
        autostart: bool = False
    ) -> Dict:
        """
        Chama GET /c/{channelId}/icp/v3/authentications (server-side).
        Retorna ClearancesResult com lista de provedores disponíveis.
        
        Se autostart=True, a API retorna HTTP 302 diretamente.
        """
        if not http_client:
            raise RuntimeError("Módulo 'requests' não disponível")

        params = {
            'secret_data': code_challenge,
            'secret_type': 'code_challenge',
            'callback_uri': callback_uri,
            'credential_lifetime': str(credential_lifetime),
            'clearance_lifetime': str(clearance_lifetime),
        }
        if subject_key:
            params['subject_key'] = subject_key
            params['subject_type'] = 'CPF'
        if autostart:
            params['autostart'] = 'true'

        url = f"{INTEGRAICP_BASE_URL}/c/{self.channel_id}/icp/v3/authentications"
        logger.info(f"IntegraICP GET /authentications — subject_key={subject_key or 'all'}")

        resp = http_client.get(url, params=params, timeout=30, allow_redirects=False)

        # HTTP 302 → autostart ativado, retorna URL de redirect
        if resp.status_code == 302:
            return {
                'redirect': True,
                'redirect_url': resp.headers.get('Location', ''),
                'status_code': 302
            }

        if resp.status_code == 200:
            data = resp.json()
            return data
        
        # Erro
        error_data = {}
        try:
            error_data = resp.json()
        except Exception:
            pass
        logger.error(f"IntegraICP /authentications erro {resp.status_code}: {error_data}")
        return {'error': error_data, 'status_code': resp.status_code}

    def get_authentications_url(
        self,
        code_challenge: str,
        callback_uri: str,
        subject_key: str = None,
        credential_lifetime: int = 3600,
        autostart: bool = False
    ) -> str:
        """
        Monta a URL para GET /authentications (para redirect no browser).
        Usado quando queremos que o browser do médico acesse diretamente.
        """
        url = (
            f"{INTEGRAICP_BASE_URL}/c/{self.channel_id}/icp/v3/authentications"
            f"?secret_data={code_challenge}"
            f"&secret_type=code_challenge"
            f"&callback_uri={quote(callback_uri, safe='')}"
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

    # ─── 2. GET /credentials — Obter dados do certificado ───────────
    def get_credential(self, credential_id: str, code_verifier: str) -> Dict:
        """
        Chama GET /c/{channelId}/icp/v3/credentials/{credentialId} (server-side).
        Usa code_verifier (não code_challenge) conforme RFC 7636.
        Retorna CredentialResult com dados do certificado digital.
        """
        if not http_client:
            raise RuntimeError("Módulo 'requests' não disponível")

        url = f"{INTEGRAICP_BASE_URL}/c/{self.channel_id}/icp/v3/credentials/{credential_id}"
        params = {
            'secret_data': code_verifier,
            'secret_type': 'code_verifier'
        }
        logger.info(f"IntegraICP GET /credentials/{credential_id}")

        resp = http_client.get(url, params=params, timeout=30)

        if resp.status_code == 200:
            return resp.json()

        error_data = {}
        try:
            error_data = resp.json()
        except Exception:
            pass
        logger.error(f"IntegraICP /credentials erro {resp.status_code}: {error_data}")
        return {'error': error_data, 'status_code': resp.status_code}

    # ─── 3. POST /signatures — Assinar documentos ───────────────────
    def sign_documents(
        self,
        credential_id: str,
        code_verifier: str,
        documents: List[Dict],
        signature_policy: str = "CMS"
    ) -> Dict:
        """
        Chama POST /c/{channelId}/icp/v3/signatures (server-side).
        
        Args:
            credential_id: CredentialId recebido após autenticação
            code_verifier: Código verificador PKCE (o mesmo usado em /authentications como challenge)
            documents: Lista de dicts com:
                - content_id: ID do documento
                - content_digest: SHA256 em Base64 (padrão, não URL-encoded)
                - description: Descrição do conteúdo
              OU:
                - content_bytes: bytes do conteúdo (SHA256 será calculado)
              OU:
                - content_hash_hex: hash SHA256 em hexadecimal (será convertido para Base64)
            signature_policy: "RAW" ou "CMS" (padrão CMS)
        """
        if not http_client:
            raise RuntimeError("Módulo 'requests' não disponível")

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

        payload = {
            "credentialId": credential_id,
            "secretType": "code_verifier",
            "secretData": code_verifier,
            "requests": requests_list
        }

        url = f"{INTEGRAICP_BASE_URL}/c/{self.channel_id}/icp/v3/signatures"
        logger.info(f"IntegraICP POST /signatures — {len(requests_list)} documento(s)")

        resp = http_client.post(url, json=payload, timeout=60)

        if resp.status_code == 200:
            return resp.json()

        error_data = {}
        try:
            error_data = resp.json()
        except Exception:
            pass
        logger.error(f"IntegraICP /signatures erro {resp.status_code}: {error_data}")
        return {'error': error_data, 'status_code': resp.status_code}

    # ─── Helpers ─────────────────────────────────────────────────────
    @staticmethod
    def calculate_sha256_b64(content: bytes) -> str:
        """Calcula SHA256 e codifica em Base64 standard (não URL-encoded). Padrão IntegraICP."""
        sha = hashlib.sha256(content).digest()
        return base64.b64encode(sha).decode('ascii')

    @staticmethod
    def calculate_sha256_hex(content: str) -> str:
        """Calcula SHA256 hexadecimal de uma string."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado com channel_id."""
        return bool(self.channel_id)
