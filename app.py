from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict
from dotenv import load_dotenv

from flask import Flask, jsonify, request, send_from_directory, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import json
import uuid
import logging
import requests as http_requests

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from asaas_integration_v2 import AsaasIntegration, criar_pagamento_completo
    logger.info("✅ Asaas Integration V2 importado com sucesso")
except ImportError:
    try:
        from asaas_integration import AsaasIntegration, criar_link_pagamento_completo as criar_pagamento_completo
        logger.warning("⚠️ Usando Asaas Integration V1")
    except ImportError:
        AsaasIntegration = None
        criar_pagamento_completo = None
        logger.error("❌ Asaas Integration não disponível - modo fallback")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data.db")

app = Flask(__name__)
app.secret_key = os.environ.get("ON_MEDICINA_SECRET", "on-medicina-secret")

# ===== SESSION / COOKIE CONFIG (ngrok & HTTPS proxies) =====
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Trust reverse-proxy headers so Flask sees HTTPS
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_for=1)

# ===== CONFIGURAÇÃO ASAAS =====
ASAAS_API_KEY = os.environ.get("ASAAS_API_KEY", "")
ASAAS_BASE_URL = os.environ.get("ASAAS_BASE_URL", "https://api.asaas.com/v3")
ASAAS_WEBHOOK_URL = os.environ.get("ASAAS_WEBHOOK_URL", "https://app.onmedicinainternacional.com/comercial/webhooks")
ASAAS_ENVIRONMENT = os.environ.get("ASAAS_ENVIRONMENT", "production")

if ASAAS_API_KEY:
    logger.info(f"✅ Token Asaas configurado - Ambiente: {ASAAS_ENVIRONMENT}")
else:
    logger.warning("⚠️ Token Asaas não configurado (.env)")

# doctors data and uploads
DATA_DIR = os.path.join(BASE_DIR, 'data')
DOCTORS_FILE = os.path.join(DATA_DIR, 'doctors.json')
LEADS_FILE = os.path.join(DATA_DIR, 'leads.json')
MEDICAMENTOS_FILE = os.path.join(DATA_DIR, 'medicamentos.json')
CENTROS_CUSTO_FILE = os.path.join(DATA_DIR, 'centros_custo.json')
PLANO_CONTAS_FILE = os.path.join(DATA_DIR, 'plano_contas.json')
FLUXO_CAIXA_FILE = os.path.join(DATA_DIR, 'fluxo_caixa.json')
CONCILIACAO_FILE = os.path.join(DATA_DIR, 'conciliacao.json')
CONSULTAS_FILE = os.path.join(DATA_DIR, 'consultas.json')
AGENDAMENTOS_FILE = os.path.join(DATA_DIR, 'agendamentos.json')
AVALIACOES_FILE = os.path.join(DATA_DIR, 'avaliacoes.json')
AGENDA_MEDICA_FILE = os.path.join(DATA_DIR, 'agenda_medica.json')
PACIENTES_FILE = os.path.join(DATA_DIR, 'pacientes.json')
PRONTUARIO_FILE = os.path.join(DATA_DIR, 'prontuarios.json')
TIMELINE_FILE = os.path.join(DATA_DIR, 'timeline_pacientes.json')
FICHAS_FILE = os.path.join(DATA_DIR, 'fichas_atendimento.json')
PRESCRICOES_FILE = os.path.join(DATA_DIR, 'prescricoes.json')
LAUDOS_FILE = os.path.join(DATA_DIR, 'laudos.json')
FORNECEDORES_FILE = os.path.join(DATA_DIR, 'fornecedores.json')
WEBHOOKS_CONFIG_FILE = os.path.join(DATA_DIR, 'webhooks_config.json')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

def load_doctors():
    if not os.path.exists(DOCTORS_FILE):
        return []
    try:
        with open(DOCTORS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_doctors(docs):
    with open(DOCTORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)


def _load_json_file(path, default=None):
    if default is None:
        default = []
    if not os.path.exists(path):
        return default if callable(default) else (list(default) if isinstance(default, list) else dict(default))
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return default if callable(default) else (list(default) if isinstance(default, list) else dict(default))


def _save_json_file(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_consultas():
    return _load_json_file(CONSULTAS_FILE, [])

def save_consultas(data):
    _save_json_file(CONSULTAS_FILE, data)

def load_agendamentos():
    return _load_json_file(AGENDAMENTOS_FILE, [])

def save_agendamentos(data):
    _save_json_file(AGENDAMENTOS_FILE, data)

def load_agenda_medica():
    return _load_json_file(AGENDA_MEDICA_FILE, [])

def save_agenda_medica(data):
    _save_json_file(AGENDA_MEDICA_FILE, data)

def load_avaliacoes():
    return _load_json_file(AVALIACOES_FILE, [])

def save_avaliacoes(data):
    _save_json_file(AVALIACOES_FILE, data)

def get_next_doctor_id():
    """Generate next sequential doctor ID (0001, 0002, etc)"""
    docs = load_doctors()
    if not docs:
        return "0001"
    # Find max numeric ID
    max_id = 0
    for doc in docs:
        try:
            doc_id = int(doc.get('id', '0'))
            if doc_id > max_id:
                max_id = doc_id
        except (ValueError, TypeError):
            pass
    return str(max_id + 1).zfill(4)


def load_leads():
    if not os.path.exists(LEADS_FILE):
        return []
    try:
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_leads(leads):
    with open(LEADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

def get_next_lead_id():
    """Generate next sequential lead ID (01, 02, etc)"""
    leads = load_leads()
    if not leads:
        return "01"
    # Find max numeric ID
    max_id = 0
    for lead in leads:
        try:
            lead_id = int(lead.get('id', '0'))
            if lead_id > max_id:
                max_id = lead_id
        except (ValueError, TypeError):
            pass
    return str(max_id + 1).zfill(2)

def load_pacientes():
    return _load_json_file(PACIENTES_FILE, [])

def save_pacientes(data):
    _save_json_file(PACIENTES_FILE, data)

def load_prontuarios():
    return _load_json_file(PRONTUARIO_FILE, [])

def save_prontuarios(data):
    _save_json_file(PRONTUARIO_FILE, data)

def load_timeline():
    return _load_json_file(TIMELINE_FILE, [])

def save_timeline(data):
    _save_json_file(TIMELINE_FILE, data)

def load_fichas():
    return _load_json_file(FICHAS_FILE, {})

def save_fichas(data):
    _save_json_file(FICHAS_FILE, data)

def load_prescricoes():
    return _load_json_file(PRESCRICOES_FILE, [])

def save_prescricoes(data):
    _save_json_file(PRESCRICOES_FILE, data)

def load_laudos():
    return _load_json_file(LAUDOS_FILE, [])

def save_laudos(data):
    _save_json_file(LAUDOS_FILE, data)

def load_fornecedores():
    return _load_json_file(FORNECEDORES_FILE, [])

def save_fornecedores(data):
    _save_json_file(FORNECEDORES_FILE, data)

def load_webhooks_config():
    return _load_json_file(WEBHOOKS_CONFIG_FILE, {'prescricao_url': '', 'prescricao_ativo': False})

def save_webhooks_config(data):
    _save_json_file(WEBHOOKS_CONFIG_FILE, data)

def get_next_paciente_id():
    pacientes = load_pacientes()
    if not pacientes:
        return '001'
    max_id = 0
    for p in pacientes:
        try:
            raw = p.get('id', '0').replace('PAC', '')
            num = int(raw)
            if num > max_id:
                max_id = num
        except (ValueError, TypeError):
            pass
    return str(max_id + 1).zfill(3)

def add_timeline_event(paciente_id, tipo, titulo, descricao='', dados=None):
    """Add an event to patient timeline"""
    tl = load_timeline()
    event = {
        'id': f'TL{len(tl)+1:05d}',
        'paciente_id': paciente_id,
        'tipo': tipo,
        'titulo': titulo,
        'descricao': descricao,
        'dados': dados or {},
        'data': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    tl.append(event)
    save_timeline(tl)
    return event

def converter_lead_para_paciente(lead_id):
    """Convert a lead to a patient after payment confirmation"""
    leads = load_leads()
    lead = next((l for l in leads if str(l.get('id')) == str(lead_id)), None)
    if not lead:
        return None
    
    pacientes = load_pacientes()
    # Check if already converted
    existing = next((p for p in pacientes if str(p.get('lead_id')) == str(lead_id)), None)
    if existing:
        return existing
    
    pac_id = get_next_paciente_id()
    import hashlib, secrets
    token = secrets.token_urlsafe(32)
    
    paciente = {
        'id': pac_id,
        'lead_id': str(lead_id),
        'nome': lead.get('name', lead.get('nome', lead.get('nome_completo', ''))),
        'cpf': lead.get('cpf', ''),
        'data_nascimento': lead.get('dob', lead.get('data_nascimento', '')),
        'sexo': lead.get('sexo', ''),
        'idade': lead.get('idade', ''),
        'foto_url': lead.get('foto_url', ''),
        'convenio': lead.get('convenio', ''),
        'email': lead.get('email', ''),
        'telefone': lead.get('phone', lead.get('telefone', '')),
        'endereco': lead.get('address', lead.get('endereco', '')),
        'responsavel_nome': lead.get('guardian_name', lead.get('nome_responsavel', '')),
        'responsavel_cpf': lead.get('guardian_cpf', lead.get('cpf_responsavel', '')),
        'diagnostico_atual': lead.get('condition_main', lead.get('condicao_principal', '')),
        'medico_responsavel_id': lead.get('medico_id', ''),
        'medico_responsavel_nome': lead.get('medico_nome', ''),
        'status': 'ativo',
        'kanban_etapa': 'formulario_anamnese',
        'pagamento_confirmado': True,
        'anamnese_preenchida': False,
        'documentos_enviados': False,
        'cadastro_completo': False,
        'token_acesso': token,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        # Clinical data from lead
        'peso': lead.get('weight', lead.get('peso', '')),
        'sintomas': lead.get('symptoms', lead.get('sintomas', '')),
        'diagnosticos_previos': lead.get('diagnosis_prev', lead.get('diagnosticos_previos', '')),
        'alergias': lead.get('diagnosis_allergies', lead.get('alergias', '')),
        'historico_familiar': lead.get('family_history', lead.get('historico_familiar', '')),
        'medicacoes': lead.get('medications', lead.get('medicacoes', '')),
        'cirurgias': lead.get('surgeries', lead.get('cirurgias', '')),
        'objetivo_consulta': lead.get('consultation_objective', lead.get('objetivo_consulta', '')),
        'exames_recentes': lead.get('recent_exams', lead.get('exames_recentes', ''))
    }
    
    pacientes.append(paciente)
    save_pacientes(pacientes)
    
    # Update lead status
    for l in leads:
        if str(l.get('id')) == str(lead_id):
            l['status'] = 'convertido'
            l['paciente_id'] = pac_id
            break
    save_leads(leads)
    
    # Add timeline event
    add_timeline_event(pac_id, 'cadastro', 'Paciente cadastrado',
        f'Paciente convertido do lead #{lead_id} apos confirmacao de pagamento')
    
    return paciente

def load_medicamentos():
    if not os.path.exists(MEDICAMENTOS_FILE):
        return []
    try:
        with open(MEDICAMENTOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_medicamentos(medicamentos):
    with open(MEDICAMENTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(medicamentos, f, ensure_ascii=False, indent=2)

def get_next_medicamento_id():
    """Generate next sequential medicamento ID (001, 002, etc)"""
    medicamentos = load_medicamentos()
    if not medicamentos:
        return "001"
    # Find max numeric ID
    max_id = 0
    for med in medicamentos:
        try:
            med_id = int(med.get('id', '0'))
            if med_id > max_id:
                max_id = med_id
        except (ValueError, TypeError):
            pass
    return str(max_id + 1).zfill(3)


# ===== FINANCIAL DATA HELPERS =====
def load_centros_custo():
    if not os.path.exists(CENTROS_CUSTO_FILE):
        return {"grupos": []}
    try:
        with open(CENTROS_CUSTO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"grupos": []}

def save_centros_custo(data):
    with open(CENTROS_CUSTO_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_plano_contas():
    if not os.path.exists(PLANO_CONTAS_FILE):
        return {"plano_contas": []}
    try:
        with open(PLANO_CONTAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"plano_contas": []}

def save_plano_contas(data):
    with open(PLANO_CONTAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_fluxo_caixa():
    if not os.path.exists(FLUXO_CAIXA_FILE):
        return []
    try:
        with open(FLUXO_CAIXA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_fluxo_caixa(data):
    with open(FLUXO_CAIXA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_conciliacao():
    if not os.path.exists(CONCILIACAO_FILE):
        return {"bancos": [], "movimentos": []}
    try:
        with open(CONCILIACAO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"bancos": [], "movimentos": []}

def save_conciliacao(data):
    with open(CONCILIACAO_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route('/api/doctors', methods=['GET'])
def list_doctors():
    return jsonify(load_doctors())


@app.route('/api/doctors', methods=['POST'])
def create_doctor():
    docs = load_doctors()
    doc = {}
    # collect form fields
    for k in request.form:
        doc[k] = request.form.get(k)
    doc['id'] = get_next_doctor_id()
    doc['created_at'] = doc.get('created_at') or datetime.now(timezone.utc).isoformat()

    # Hash password if provided
    raw_pw = doc.pop('password', None) or request.form.get('password')
    if raw_pw:
        doc['password_hash'] = generate_password_hash(raw_pw)
    doc['status'] = doc.get('status', 'pendente')  # pendente, aprovado, rejeitado

    # handle photo
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            target_dir = os.path.join(UPLOADS_DIR, doc['id'])
            os.makedirs(target_dir, exist_ok=True)
            path = os.path.join(target_dir, filename)
            photo.save(path)
            doc['photo_url'] = '/uploads/' + doc['id'] + '/' + filename

    crm_files = request.files.getlist('crm_files')
    crm_saved = []
    for f in crm_files:
        if f and f.filename:
            filename = secure_filename(f.filename)
            target_dir = os.path.join(UPLOADS_DIR, doc['id'])
            os.makedirs(target_dir, exist_ok=True)
            path = os.path.join(target_dir, filename)
            f.save(path)
            crm_saved.append({'filename': filename})
    if crm_saved:
        doc['crm_docs'] = crm_saved

    docs.append(doc)
    save_doctors(docs)
    return jsonify(doc), 201


@app.route('/api/doctors/<doc_id>', methods=['PUT'])
def update_doctor(doc_id):
    docs = load_doctors()
    idx = next((i for i, d in enumerate(docs) if d.get('id') == doc_id), None)
    if idx is None:
        return jsonify({'error': 'not found'}), 404
    doc = docs[idx]
    for k in request.form:
        doc[k] = request.form.get(k)
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            target_dir = os.path.join(UPLOADS_DIR, doc_id)
            os.makedirs(target_dir, exist_ok=True)
            path = os.path.join(target_dir, filename)
            photo.save(path)
            doc['photo_url'] = '/uploads/' + doc_id + '/' + filename
    save_doctors(docs)
    return jsonify(doc)


@app.route('/api/doctors/<doc_id>', methods=['DELETE'])
def delete_doctor(doc_id):
    docs = load_doctors()
    docs = [d for d in docs if d.get('id') != doc_id]
    save_doctors(docs)
    return jsonify({'ok': True})


# ===== LEADS (Pacientes) API =====

@app.route('/api/leads', methods=['GET'])
def list_leads():
    return jsonify(load_leads())


@app.route('/api/leads', methods=['POST'])
def create_lead():
    leads = load_leads()
    # Get data from JSON body
    data = request.get_json(silent=True) or {}
    lead = {}
    for k, v in data.items():
        lead[k] = v
    lead['id'] = get_next_lead_id()
    lead['created_at'] = lead.get('created_at') or datetime.now(timezone.utc).isoformat()

    leads.append(lead)
    save_leads(leads)
    return jsonify(lead), 201


@app.route('/api/leads/<lead_id>', methods=['GET'])
def get_lead(lead_id):
    leads = load_leads()
    lead = next((l for l in leads if l.get('id') == lead_id), None)
    if not lead:
        return jsonify({'error': 'not found'}), 404
    return jsonify(lead)


@app.route('/api/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    leads = load_leads()
    idx = next((i for i, l in enumerate(leads) if l.get('id') == lead_id), None)
    if idx is None:
        return jsonify({'error': 'not found'}), 404
    lead = leads[idx]
    # update fields from request
    data = request.get_json(silent=True) or {}
    for k, v in data.items():
        if k not in ['id', 'created_at']:
            lead[k] = v
    save_leads(leads)
    return jsonify(lead)


@app.route('/api/leads/<lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    leads = load_leads()
    leads = [l for l in leads if l.get('id') != lead_id]
    save_leads(leads)
    return jsonify({'ok': True})


@app.route('/uploads/<doc_id>/<filename>')
def serve_upload(doc_id, filename):
    directory = os.path.join(UPLOADS_DIR, doc_id)
    return send_from_directory(directory, filename)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                payment_data TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def seed_admin() -> None:
    admin_email = "gabrielamultiplace@gmail.com"
    admin_password = "@On2025@"
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (admin_email,)
        ).fetchone()
        if existing:
            return
        conn.execute(
            """
            INSERT INTO users (name, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Gabriela Admin",
                admin_email,
                generate_password_hash(admin_password),
                "admin",
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()


def ensure_db_ready() -> None:
    try:
        init_db()
        seed_admin()
        logger.info("✅ Banco de dados inicializado")
    except Exception as exc:
        logger.error(f"❌ Falha ao inicializar o banco: {exc}")


def user_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "role": row["role"],
        "created_at": row["created_at"],
    }


def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    return has_upper and has_lower and has_digit


@app.after_request
def add_no_cache_headers(response):
    """Force no-cache on ALL responses to prevent stale content"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    if 'ETag' in response.headers:
        del response.headers['ETag']
    if 'Last-Modified' in response.headers:
        del response.headers['Last-Modified']
    return response


@app.route("/")
def index() -> Any:
    # Read and return directly to avoid send_from_directory caching
    html_path = os.path.join(BASE_DIR, "index.html")
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    from flask import make_response
    resp = make_response(content)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp


@app.route("/cleanup_localstorage.html")
def cleanup_localstorage() -> str:
    """Página para limpar localStorage acumulado"""
    return """<!DOCTYPE html>
<html>
<head>
    <title>Limpeza de Cache</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 500px; margin: 0 auto; }
        h1 { color: #0E4D42; }
        p { color: #666; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #0E4D42; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .success { color: #4CAF50; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧹 Limpeza Completa de Cache</h1>
        <p>Removendo todos os dados acumulados...</p>
        <div class="spinner"></div>
        <p id="status">Aguarde...</p>
    </div>
    <script>
        try {
            // Listar todas as chaves do localStorage
            const keys = Object.keys(localStorage);
            console.log('Chaves no localStorage:', keys);
            
            // Remover TUDO do localStorage
            localStorage.clear();
            sessionStorage.clear();
            
            // Limpar IndexedDB se houver
            if (window.indexedDB) {
                const dbs = await indexedDB.databases();
                dbs.forEach(db => {
                    indexedDB.deleteDatabase(db.name);
                });
            }
            
            // Limpar Service Workers
            if (navigator.serviceWorker) {
                navigator.serviceWorker.getRegistrations().then(regs => {
                    regs.forEach(reg => reg.unregister());
                });
            }
            
            // Limpar cookies
            document.cookie.split(";").forEach(function(c) { 
                document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
            });
            
            document.getElementById('status').innerHTML = '<span class="success">✅ Cache completamente limpo!</span><br><br>Você será redirecionado em 2 segundos...';
            
            setTimeout(function() {
                window.location.href = '/';
            }, 2000);
        } catch(e) {
            document.getElementById('status').innerHTML = '<span style="color: red;">❌ Erro: ' + e.message + '</span><br>Recarregando...';
            setTimeout(() => location.reload(), 2000);
        }
    </script>
</body>
</html>"""


@app.route("/api/login", methods=["POST"])
def login() -> Any:
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not email or not password:
        return jsonify({"message": "Informe e-mail e senha."}), 400

    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"message": "Credenciais inválidas."}), 401

    session["user_id"] = row["id"]
    return jsonify({"user": user_from_row(row)})


@app.route("/api/logout", methods=["POST"])
def logout() -> Any:
    session.pop("user_id", None)
    return jsonify({"ok": True})


@app.route("/api/me", methods=["GET"])
def me() -> Any:
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Não autenticado."}), 401

    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if not row:
        session.pop("user_id", None)
        return jsonify({"message": "Sessão inválida."}), 401

    return jsonify({"user": user_from_row(row)})


@app.route("/api/users", methods=["GET"])
def list_users() -> Any:
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Não autenticado."}), 401

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()

    return jsonify({"users": [user_from_row(row) for row in rows]})


@app.route("/api/users", methods=["POST"])
def create_user() -> Any:
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Não autenticado."}), 401

    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    role = str(payload.get("role", "usuario")).strip() or "usuario"

    if not name or not email or not password:
        return jsonify({"message": "Preencha nome, e-mail e senha."}), 400

    if not is_strong_password(password):
        return jsonify({
            "message": "A senha deve ter 8+ caracteres, com maiúscula, minúscula e número."
        }), 400

    with get_db() as conn:
        try:
            conn.execute(
                """
                INSERT INTO users (name, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    generate_password_hash(password),
                    role,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({"message": "E-mail já cadastrado."}), 409

    return jsonify({"ok": True})


@app.route("/api/users/reset-password", methods=["POST"])
def reset_password() -> Any:
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Não autenticado."}), 401

    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    new_password = str(payload.get("new_password", ""))

    if not email or not new_password:
        return jsonify({"message": "Informe e-mail e nova senha."}), 400

    if not is_strong_password(new_password):
        return jsonify({
            "message": "A senha deve ter 8+ caracteres, com maiúscula, minúscula e número."
        }), 400

    with get_db() as conn:
        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            return jsonify({"message": "Usuário não encontrado."}), 404
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), row["id"]),
        )
        conn.commit()

    return jsonify({"ok": True})


# ===== MEDICAMENTOS API =====
@app.route('/api/medicamentos', methods=['GET'])
def list_medicamentos():
    return jsonify(load_medicamentos())


@app.route('/api/medicamentos', methods=['POST'])
def create_medicamento():
    medicamentos = load_medicamentos()
    data = request.get_json(silent=True) or {}
    medicamento = {}
    for k, v in data.items():
        medicamento[k] = v
    medicamento['id'] = medicamento.get('id') or get_next_medicamento_id()
    medicamento['created_at'] = medicamento.get('created_at') or datetime.now(timezone.utc).isoformat()

    medicamentos.append(medicamento)
    save_medicamentos(medicamentos)
    return jsonify(medicamento), 201


@app.route('/api/medicamentos/<medicamento_id>', methods=['GET'])
def get_medicamento(medicamento_id):
    medicamentos = load_medicamentos()
    medicamento = next((m for m in medicamentos if m.get('id') == medicamento_id), None)
    if not medicamento:
        return jsonify({'error': 'not found'}), 404
    return jsonify(medicamento)


@app.route('/api/medicamentos/<medicamento_id>', methods=['PUT'])
def update_medicamento(medicamento_id):
    medicamentos = load_medicamentos()
    idx = next((i for i, m in enumerate(medicamentos) if m.get('id') == medicamento_id), None)
    if idx is None:
        return jsonify({'error': 'not found'}), 404
    
    data = request.get_json(silent=True) or {}
    medicamento = medicamentos[idx]
    for k, v in data.items():
        if k != 'id':  # Don't update ID
            medicamento[k] = v
    
    medicamentos[idx] = medicamento
    save_medicamentos(medicamentos)
    return jsonify(medicamento)


@app.route('/api/medicamentos/<medicamento_id>', methods=['DELETE'])
def delete_medicamento(medicamento_id):
    medicamentos = load_medicamentos()
    medicamentos = [m for m in medicamentos if m.get('id') != medicamento_id]
    save_medicamentos(medicamentos)
    return jsonify({'ok': True})


@app.route('/api/debug/medicamentos', methods=['GET'])
def debug_medicamentos():
    """Debug endpoint to check medicamentos status"""
    med_data = load_medicamentos()
    return jsonify({
        'total': len(med_data),
        'sample': med_data[:3] if med_data else [],
        'file_path': MEDICAMENTOS_FILE,
        'file_exists': os.path.exists(MEDICAMENTOS_FILE),
        'file_size': os.path.getsize(MEDICAMENTOS_FILE) if os.path.exists(MEDICAMENTOS_FILE) else 0
    })


# ===== COTAÇÃO / EXCHANGE RATE API =====
_cotacao_cache = {}  # {moeda: {data, timestamp}}

def _fetch_cotacoes_batch(moedas_list):
    """Fetch multiple currencies - tries AwesomeAPI first, then fallbacks"""
    import time
    results = {}

    # Strategy 1: AwesomeAPI (batch call)
    try:
        pairs = ','.join([f'{m}-BRL' for m in moedas_list])
        url = f'https://economia.awesomeapi.com.br/last/{pairs}'
        resp = http_requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for moeda in moedas_list:
                key = f'{moeda}BRL'
                if key in data:
                    info = data[key]
                    result = {
                        'moeda': moeda,
                        'bid': float(info.get('bid', 0)),
                        'ask': float(info.get('ask', 0)),
                        'high': float(info.get('high', 0)),
                        'low': float(info.get('low', 0)),
                        'nome': info.get('name', ''),
                        'timestamp': info.get('create_date', datetime.now(timezone.utc).isoformat())
                    }
                    results[moeda] = result
                    _cotacao_cache[moeda] = {'data': result, 'timestamp': time.time()}
            if results:
                return results
    except Exception as e:
        logger.warning(f'AwesomeAPI falhou: {e}')

    # Strategy 2: ExchangeRate-API (free, no key)
    try:
        url = 'https://open.er-api.com/v6/latest/BRL'
        resp = http_requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            rates = data.get('rates', {})
            for moeda in moedas_list:
                if moeda in rates and rates[moeda] > 0:
                    bid = 1.0 / rates[moeda]  # Convert from BRL-per-foreign to foreign-per-BRL
                    result = {
                        'moeda': moeda,
                        'bid': round(bid, 4),
                        'ask': round(bid, 4),
                        'high': 0, 'low': 0,
                        'nome': f'{moeda}/BRL',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    results[moeda] = result
                    _cotacao_cache[moeda] = {'data': result, 'timestamp': time.time()}
            if results:
                return results
    except Exception as e:
        logger.warning(f'ExchangeRate-API falhou: {e}')

    # Strategy 3: exchangerate-api.com (free tier)
    try:
        url = 'https://api.exchangerate-api.com/v4/latest/BRL'
        resp = http_requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            rates = data.get('rates', {})
            for moeda in moedas_list:
                if moeda in rates and rates[moeda] > 0:
                    bid = 1.0 / rates[moeda]
                    result = {
                        'moeda': moeda,
                        'bid': round(bid, 4),
                        'ask': round(bid, 4),
                        'high': 0, 'low': 0,
                        'nome': f'{moeda}/BRL',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    results[moeda] = result
                    _cotacao_cache[moeda] = {'data': result, 'timestamp': time.time()}
            if results:
                return results
    except Exception as e:
        logger.warning(f'exchangerate-api.com falhou: {e}')

    return results


@app.route('/api/cotacao/<moeda>', methods=['GET'])
def get_cotacao(moeda):
    """Fetch exchange rate from AwesomeAPI. moeda = USD, EUR, GBP, CAD, etc."""
    import time
    moeda = moeda.upper()

    if moeda == 'BRL':
        return jsonify({'moeda': 'BRL', 'bid': 1.0, 'ask': 1.0, 'nome': 'Real Brasileiro', 'timestamp': datetime.now(timezone.utc).isoformat()})

    # Cache for 30 min to avoid excessive API calls
    cached = _cotacao_cache.get(moeda)
    if cached and (time.time() - cached['timestamp']) < 1800:
        return jsonify(cached['data'])

    results = _fetch_cotacoes_batch([moeda])
    if moeda in results:
        return jsonify(results[moeda])

    # Fallback: return cached even if expired
    if cached:
        return jsonify(cached['data'])

    return jsonify({'error': f'Não foi possível buscar cotação para {moeda}. Tente novamente em alguns segundos.'}), 502


@app.route('/api/cotacao', methods=['GET'])
def get_cotacoes_all():
    """Fetch exchange rates for main currencies in a single batch call"""
    import time
    moedas = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'CHF']
    results = {'BRL': {'moeda': 'BRL', 'bid': 1.0, 'nome': 'Real Brasileiro'}}

    # Check which ones need fetching
    need_fetch = []
    for moeda in moedas:
        cached = _cotacao_cache.get(moeda)
        if cached and (time.time() - cached['timestamp']) < 1800:
            results[moeda] = cached['data']
        else:
            need_fetch.append(moeda)

    # Fetch all needed in a single API call
    if need_fetch:
        fetched = _fetch_cotacoes_batch(need_fetch)
        results.update(fetched)

    return jsonify(results)


# ===== CENTROS DE CUSTO API =====
@app.route('/api/centros-custo', methods=['GET'])
def get_centros_custo():
    return jsonify(load_centros_custo())

@app.route('/api/centros-custo', methods=['POST'])
def add_centro_custo():
    data = load_centros_custo()
    body = request.get_json(silent=True) or {}
    grupo = {
        "id": max([g.get("id", 0) for g in data.get("grupos", [])] or [0]) + 1,
        "nome": body.get("nome", "Novo Grupo"),
        "subgrupos": body.get("subgrupos", [])
    }
    data.setdefault("grupos", []).append(grupo)
    save_centros_custo(data)
    return jsonify(grupo), 201

@app.route('/api/centros-custo/<int:grupo_id>', methods=['PUT'])
def update_centro_custo(grupo_id):
    data = load_centros_custo()
    grupo = next((g for g in data.get("grupos", []) if g.get("id") == grupo_id), None)
    if not grupo:
        return jsonify({"error": "not found"}), 404
    body = request.get_json(silent=True) or {}
    grupo["nome"] = body.get("nome", grupo["nome"])
    if "subgrupos" in body:
        grupo["subgrupos"] = body["subgrupos"]
    save_centros_custo(data)
    return jsonify(grupo)

@app.route('/api/centros-custo/<int:grupo_id>', methods=['DELETE'])
def delete_centro_custo(grupo_id):
    data = load_centros_custo()
    data["grupos"] = [g for g in data.get("grupos", []) if g.get("id") != grupo_id]
    save_centros_custo(data)
    return jsonify({"ok": True})

@app.route('/api/centros-custo/<int:grupo_id>/subgrupos', methods=['POST'])
def add_subgrupo(grupo_id):
    data = load_centros_custo()
    grupo = next((g for g in data.get("grupos", []) if g.get("id") == grupo_id), None)
    if not grupo:
        return jsonify({"error": "grupo not found"}), 404
    body = request.get_json(silent=True) or {}
    all_sub_ids = [s.get("id", 0) for g in data.get("grupos", []) for s in g.get("subgrupos", [])]
    new_id = max(all_sub_ids or [0]) + 1
    sub = {"id": new_id, "nome": body.get("nome", "Novo Subgrupo"), "status": body.get("status", "Ativo")}
    grupo.setdefault("subgrupos", []).append(sub)
    save_centros_custo(data)
    return jsonify(sub), 201


# ===== PLANO DE CONTAS API =====
@app.route('/api/plano-contas', methods=['GET'])
def get_plano_contas():
    return jsonify(load_plano_contas())

@app.route('/api/plano-contas', methods=['POST'])
def add_plano_conta():
    data = load_plano_contas()
    body = request.get_json(silent=True) or {}
    conta = {
        "id": max([c.get("id", 0) for c in data.get("plano_contas", [])] or [0]) + 1,
        "grupo": body.get("grupo", ""),
        "categoria": body.get("categoria", ""),
        "subcategorias": body.get("subcategorias", [])
    }
    data.setdefault("plano_contas", []).append(conta)
    save_plano_contas(data)
    return jsonify(conta), 201

@app.route('/api/plano-contas/<int:conta_id>', methods=['PUT'])
def update_plano_conta(conta_id):
    data = load_plano_contas()
    conta = next((c for c in data.get("plano_contas", []) if c.get("id") == conta_id), None)
    if not conta:
        return jsonify({"error": "not found"}), 404
    body = request.get_json(silent=True) or {}
    conta["grupo"] = body.get("grupo", conta["grupo"])
    conta["categoria"] = body.get("categoria", conta["categoria"])
    if "subcategorias" in body:
        conta["subcategorias"] = body["subcategorias"]
    save_plano_contas(data)
    return jsonify(conta)

@app.route('/api/plano-contas/<int:conta_id>', methods=['DELETE'])
def delete_plano_conta(conta_id):
    data = load_plano_contas()
    data["plano_contas"] = [c for c in data.get("plano_contas", []) if c.get("id") != conta_id]
    save_plano_contas(data)
    return jsonify({"ok": True})


# ===== FLUXO DE CAIXA API =====
@app.route('/api/fluxo-caixa', methods=['GET'])
def get_fluxo_caixa():
    return jsonify(load_fluxo_caixa())

@app.route('/api/fluxo-caixa', methods=['POST'])
def add_fluxo_movimento():
    movimentos = load_fluxo_caixa()
    body = request.get_json(silent=True) or {}
    mov = {
        "id": str(uuid.uuid4())[:8],
        "data": body.get("data", datetime.now().strftime("%Y-%m-%d")),
        "descricao": body.get("descricao", ""),
        "tipo": body.get("tipo", "entrada"),
        "valor": float(body.get("valor", 0)),
        "centro_custo": body.get("centro_custo", ""),
        "plano_conta": body.get("plano_conta", ""),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    movimentos.append(mov)
    save_fluxo_caixa(movimentos)
    return jsonify(mov), 201

@app.route('/api/fluxo-caixa/<mov_id>', methods=['DELETE'])
def delete_fluxo_movimento(mov_id):
    movimentos = load_fluxo_caixa()
    movimentos = [m for m in movimentos if m.get("id") != mov_id]
    save_fluxo_caixa(movimentos)
    return jsonify({"ok": True})


# ===== CONCILIACAO BANCARIA API =====
@app.route('/api/conciliacao', methods=['GET'])
def get_conciliacao():
    return jsonify(load_conciliacao())

@app.route('/api/conciliacao/bancos', methods=['POST'])
def add_banco():
    data = load_conciliacao()
    body = request.get_json(silent=True) or {}
    banco = {
        "id": str(uuid.uuid4())[:8],
        "nome": body.get("nome", ""),
        "agencia": body.get("agencia", ""),
        "conta": body.get("conta", ""),
        "saldo": float(body.get("saldo", 0))
    }
    data.setdefault("bancos", []).append(banco)
    save_conciliacao(data)
    return jsonify(banco), 201

@app.route('/api/conciliacao/bancos/<banco_id>', methods=['DELETE'])
def delete_banco(banco_id):
    data = load_conciliacao()
    data["bancos"] = [b for b in data.get("bancos", []) if b.get("id") != banco_id]
    save_conciliacao(data)
    return jsonify({"ok": True})

@app.route('/api/conciliacao/movimentos', methods=['POST'])
def add_conciliacao_movimento():
    data = load_conciliacao()
    body = request.get_json(silent=True) or {}
    mov = {
        "id": str(uuid.uuid4())[:8],
        "banco_id": body.get("banco_id", ""),
        "data": body.get("data", datetime.now().strftime("%Y-%m-%d")),
        "descricao": body.get("descricao", ""),
        "valor": float(body.get("valor", 0)),
        "status": body.get("status", "pendente"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    data.setdefault("movimentos", []).append(mov)
    save_conciliacao(data)
    return jsonify(mov), 201

@app.route('/api/conciliacao/movimentos/<mov_id>', methods=['PUT'])
def update_conciliacao_status(mov_id):
    data = load_conciliacao()
    mov = next((m for m in data.get("movimentos", []) if m.get("id") == mov_id), None)
    if not mov:
        return jsonify({"error": "not found"}), 404
    body = request.get_json(silent=True) or {}
    mov["status"] = body.get("status", mov["status"])
    save_conciliacao(data)
    return jsonify(mov)

@app.route('/api/conciliacao/movimentos/<mov_id>', methods=['DELETE'])
def delete_conciliacao_movimento(mov_id):
    data = load_conciliacao()
    data["movimentos"] = [m for m in data.get("movimentos", []) if m.get("id") != mov_id]
    save_conciliacao(data)
    return jsonify({"ok": True})


# ========== INTEGRAÇÃO ASAAS ==========
@app.route('/api/asaas/criar-pagamento', methods=['POST'])
def criar_pagamento_asaas():
    """
    Cria um pagamento via Asaas com opções de PIX, Boleto e Cartão
    """
    if not AsaasIntegration:
        return jsonify({'error': 'Módulo Asaas não disponível'}), 500
    
    data = request.json
    lead_id = data.get('lead_id')
    lead_name = data.get('lead_name', 'Cliente')
    lead_email = data.get('lead_email', 'noreply@onmedicina.com')
    lead_cpf = data.get('lead_cpf', '12345678901234')
    amount = float(data.get('amount', 0))
    
    if amount <= 0:
        return jsonify({'error': 'Valor inválido'}), 400
    
    try:
        lead_data = {
            'id': lead_id,
            'name': lead_name,
            'email': lead_email,
            'cpf_cnpj': lead_cpf
        }
        
        result = criar_pagamento_completo(lead_data, amount)
        
        # Salvar informações de pagamento no banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO payments 
            (lead_id, amount, status, payment_data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            lead_id,
            amount,
            'pending',
            json.dumps(result),
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        conn.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/asaas/obter-cobranca/<charge_id>', methods=['GET'])
def obter_cobranca(charge_id):
    """Obtém status de uma cobrança"""
    if not AsaasIntegration:
        return jsonify({'error': 'Módulo Asaas não disponível'}), 500
    
    try:
        asaas = AsaasIntegration()
        result = asaas.obter_cobranca(charge_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/asaas/confirmar-pagamento', methods=['POST'])
def confirmar_pagamento_asaas():
    """Confirma um pagamento após webhook"""
    if not AsaasIntegration:
        return jsonify({'error': 'Módulo Asaas não disponível'}), 500
    
    data = request.json
    charge_id = data.get('charge_id')
    lead_id = data.get('lead_id')
    
    if not charge_id:
        return jsonify({'error': 'charge_id é obrigatório'}), 400
    
    try:
        asaas = AsaasIntegration()
        charge_status = asaas.confirmar_pagamento(charge_id)
        
        if charge_status.get('payment_confirmed'):
            # Atualizar status do pagamento no banco
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE payments 
                SET status = 'confirmed'
                WHERE lead_id = ?
            ''', (lead_id,))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Pagamento confirmado com sucesso',
                'charge_id': charge_id,
                'lead_id': lead_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f"Status do pagamento: {charge_status.get('status')}",
                'charge_id': charge_id
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/asaas/webhook', methods=['POST'])
@app.route('/comercial/webhooks', methods=['POST'])
def webhook_asaas():
    """
    Webhook para receber notificações de pagamento do Asaas
    Documentação: https://docs.asaas.com/reference/webhooks
    URL configurada no Asaas: /comercial/webhooks
    """
    try:
        data = request.json
        event = data.get('event')
        charge_id = data.get('charge', {}).get('id')
        status = data.get('charge', {}).get('status')
        
        # Log do webhook
        webhook_log = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event': event,
            'charge_id': charge_id,
            'status': status,
            'data': data
        }
        
        # Salvar log
        logs_file = os.path.join(DATA_DIR, 'asaas_webhooks.json')
        logs = []
        if os.path.exists(logs_file):
            with open(logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        logs.append(webhook_log)
        with open(logs_file, 'w', encoding='utf-8') as f:
            json.dump(logs[-100:], f, ensure_ascii=False, indent=2)  # Manter últimos 100 logs
        
        # Processar eventos
        if event == 'PAYMENT_RECEIVED':
            # Pagamento recebido com sucesso
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT lead_id FROM payments WHERE payment_data LIKE ?', (f'%{charge_id}%',))
            result = cursor.fetchone()
            if result:
                lead_id = result[0]
                cursor.execute('UPDATE payments SET status = ? WHERE lead_id = ?', ('confirmed', lead_id))
                conn.commit()
            conn.close()
        
        elif event == 'PAYMENT_CONFIRMED':
            # Pagamento confirmado
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT lead_id FROM payments WHERE payment_data LIKE ?', (f'%{charge_id}%',))
            result = cursor.fetchone()
            if result:
                lead_id = result[0]
                cursor.execute('UPDATE payments SET status = ? WHERE lead_id = ?', ('confirmed', lead_id))
                conn.commit()
                # Auto-convert lead to patient
                try:
                    paciente = converter_lead_para_paciente(lead_id)
                    if paciente:
                        logger.info(f'Lead {lead_id} convertido para paciente {paciente["id"]}')
                except Exception as conv_err:
                    logger.error(f'Erro ao converter lead {lead_id}: {conv_err}')
            conn.close()
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/asaas/status-pagamento/<lead_id>', methods=['GET'])
def status_pagamento(lead_id):
    """Obtém status do pagamento de um lead"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT amount, status, payment_data, created_at
            FROM payments
            WHERE lead_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (lead_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'lead_id': lead_id,
                'amount': result[0],
                'status': result[1],
                'payment_data': json.loads(result[2]) if result[2] else {},
                'created_at': result[3]
            }), 200
        else:
            return jsonify({'error': 'Nenhum pagamento encontrado'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/asaas/teste', methods=['GET'])
def teste_asaas():
    """Endpoint de teste da integração Asaas"""
    if not AsaasIntegration:
        return jsonify({'error': 'Módulo Asaas não disponível'}), 500
    
    try:
        asaas = AsaasIntegration(sandbox=True)
        
        # Criar cliente de teste
        cliente = asaas.criar_cliente(
            'Paciente Teste',
            'teste@example.com',
            '12345678901234'
        )
        
        return jsonify({
            'success': True,
            'message': 'Integração Asaas funcionando',
            'test_customer': cliente,
            'available_billing_types': ['PIX', 'BOLETO', 'CREDIT_CARD']
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/asaas/webhook-config', methods=['GET'])
def get_webhook_config():
    """Retorna configuração de webhook do Asaas"""
    try:
        # URL do webhook baseada no host
        webhook_url = request.url_root.rstrip('/') + '/api/asaas/webhook'
        
        # Se em produção, usar URL HTTPS
        if request.host != 'localhost:5000':
            webhook_url = 'https://app.onmedicinainternacional.com/comercial/webhooks'
        
        # Token mascarado para exibição
        token_status = "✅ Configurado" if ASAAS_API_KEY else "❌ Não configurado"
        token_masked = (ASAAS_API_KEY[:10] + "..." + ASAAS_API_KEY[-6:]) if ASAAS_API_KEY else "não configurado"
        
        # Eventos disponíveis do Asaas
        available_events = [
            {
                'id': 'PAYMENT_CREATED',
                'label': 'Pagamento Criado',
                'description': 'Acionado quando um pagamento é criado',
                'enabled': True
            },
            {
                'id': 'PAYMENT_CONFIRMED',
                'label': 'Pagamento Confirmado',
                'description': 'Acionado quando um pagamento é confirmado',
                'enabled': True
            },
            {
                'id': 'PAYMENT_RECEIVED',
                'label': 'Pagamento Recebido',
                'description': 'Acionado quando o pagamento é recebido com sucesso',
                'enabled': True
            },
            {
                'id': 'PAYMENT_OVERDUE',
                'label': 'Pagamento Vencido',
                'description': 'Acionado quando um pagamento vence',
                'enabled': True
            },
            {
                'id': 'PAYMENT_REFUNDED',
                'label': 'Pagamento Reembolsado',
                'description': 'Acionado quando um pagamento é reembolsado',
                'enabled': True
            }
        ]
        
        return jsonify({
            'webhook_url': webhook_url,
            'webhook_name': 'OnPlataforma',
            'events': available_events,
            'status': 'active',
            'api_key': {
                'status': token_status,
                'masked': token_masked,
                'environment': ASAAS_ENVIRONMENT,
                'base_url': ASAAS_BASE_URL
            },
            'deployment': {
                'url': 'https://app.onmedicinainternacional.com/comercial/webhooks',
                'workers': 4,
                'server': 'Gunicorn',
                'ssl': True,
                'last_sync': '2026-02-04 16:53 UTC'
            },
            'documentation': {
                'asaas': 'https://docs.asaas.com/reference/webhooks',
                'sandbox': 'https://sandbox.asaas.com/api-docs#webhooks',
                'auth': 'https://docs.asaas.com/reference/authentication'
            },
            'test_urls': {
                'sandbox': 'https://sandbox.asaas.com',
                'production': 'https://www.asaas.com'
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Erro ao obter configuração de webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/asaas/validar-token', methods=['GET'])
def validar_token_asaas():
    """Valida se o token Asaas está configurado e funcional"""
    try:
        if not ASAAS_API_KEY:
            return jsonify({
                'valid': False,
                'message': 'Token não configurado',
                'status': '❌ Não configurado'
            }), 200
        
        # Fazer uma chamada simples à API do Asaas para validar
        import requests
        headers = {
            'access_token': ASAAS_API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{ASAAS_BASE_URL}/accounts", headers=headers, timeout=5)
        
        if response.status_code == 200:
            return jsonify({
                'valid': True,
                'message': 'Token válido e funcional',
                'status': '✅ Ativo',
                'environment': ASAAS_ENVIRONMENT
            }), 200
        else:
            return jsonify({
                'valid': False,
                'message': f'Token inválido ou expirado (Status: {response.status_code})',
                'status': '⚠️ Inválido'
            }), 200
    
    except Exception as e:
        logger.error(f"Erro ao validar token Asaas: {str(e)}")
        return jsonify({
            'valid': False,
            'message': f'Erro ao validar: {str(e)}',
            'status': '❌ Erro'
        }), 200


# ===== DOCTOR PORTAL (MODULO MEDICO) =====

@app.route('/medico')
def medico_portal():
    """Serve the doctor portal page"""
    return send_from_directory(BASE_DIR, 'medico.html')


@app.route('/api/medico/login', methods=['POST'])
def medico_login():
    """Doctor login with email/password"""
    payload = request.get_json(silent=True) or {}
    email = str(payload.get('email', '')).strip().lower()
    password = str(payload.get('password', ''))

    if not email or not password:
        return jsonify({'message': 'Informe e-mail e senha.'}), 400

    docs = load_doctors()
    doctor = next((d for d in docs if d.get('email', '').lower() == email), None)

    if not doctor:
        return jsonify({'message': 'Credenciais invalidas.'}), 401

    pw_hash = doctor.get('password_hash', '')
    if not pw_hash or not check_password_hash(pw_hash, password):
        return jsonify({'message': 'Credenciais invalidas.'}), 401

    if doctor.get('status') not in ('aprovado', 'ativo'):
        return jsonify({'message': 'Seu cadastro ainda esta pendente de aprovacao.'}), 403

    session['medico_id'] = doctor['id']
    safe = {k: v for k, v in doctor.items() if k != 'password_hash'}
    return jsonify({'doctor': safe})


@app.route('/api/medico/logout', methods=['POST'])
def medico_logout():
    session.pop('medico_id', None)
    return jsonify({'ok': True})


@app.route('/api/medico/me', methods=['GET'])
def medico_me():
    """Get current doctor session"""
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    docs = load_doctors()
    doctor = next((d for d in docs if d.get('id') == mid), None)
    if not doctor:
        session.pop('medico_id', None)
        return jsonify({'message': 'Sessao invalida.'}), 401
    safe = {k: v for k, v in doctor.items() if k != 'password_hash'}
    return jsonify({'doctor': safe})


@app.route('/api/medico/perfil', methods=['PUT'])
def medico_update_perfil():
    """Doctor updates own profile"""
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    docs = load_doctors()
    idx = next((i for i, d in enumerate(docs) if d.get('id') == mid), None)
    if idx is None:
        return jsonify({'message': 'Medico nao encontrado.'}), 404
    doc = docs[idx]
    for k in request.form:
        if k not in ('id', 'password_hash', 'created_at', 'status'):
            doc[k] = request.form.get(k)
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            target_dir = os.path.join(UPLOADS_DIR, mid)
            os.makedirs(target_dir, exist_ok=True)
            photo.save(os.path.join(target_dir, filename))
            doc['photo_url'] = '/uploads/' + mid + '/' + filename
    save_doctors(docs)
    safe = {k: v for k, v in doc.items() if k != 'password_hash'}
    return jsonify({'doctor': safe})


@app.route('/api/medico/alterar-senha', methods=['POST'])
def medico_alterar_senha():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    payload = request.get_json(silent=True) or {}
    senha_atual = payload.get('senha_atual', '')
    nova_senha = payload.get('nova_senha', '')
    if not senha_atual or not nova_senha:
        return jsonify({'message': 'Informe senha atual e nova senha.'}), 400
    if not is_strong_password(nova_senha):
        return jsonify({'message': 'A senha deve ter 8+ caracteres, com maiuscula, minuscula e numero.'}), 400
    docs = load_doctors()
    doc = next((d for d in docs if d.get('id') == mid), None)
    if not doc:
        return jsonify({'message': 'Medico nao encontrado.'}), 404
    if not check_password_hash(doc.get('password_hash', ''), senha_atual):
        return jsonify({'message': 'Senha atual incorreta.'}), 401
    doc['password_hash'] = generate_password_hash(nova_senha)
    save_doctors(docs)
    return jsonify({'ok': True})


# --- Doctor Consultations ---
@app.route('/api/medico/consultas', methods=['GET'])
def medico_consultas():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    consultas = load_consultas()
    minhas = [c for c in consultas if c.get('medico_id') == mid]
    return jsonify(minhas)


@app.route('/api/medico/consultas', methods=['POST'])
def medico_criar_consulta():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    data = request.get_json(silent=True) or {}
    consulta = {
        'id': str(uuid.uuid4())[:8],
        'medico_id': mid,
        'paciente_id': data.get('paciente_id', ''),
        'paciente_nome': data.get('paciente_nome', ''),
        'tipo': data.get('tipo', 'videochamada'),  # videochamada, chat, presencial
        'data': data.get('data', ''),
        'hora': data.get('hora', ''),
        'duracao': data.get('duracao', 30),
        'diagnostico': data.get('diagnostico', ''),
        'prescricao': data.get('prescricao', ''),
        'notas': data.get('notas', ''),
        'cid': data.get('cid', ''),
        'status': data.get('status', 'agendada'),  # agendada, em_andamento, concluida, cancelada
        'link_videochamada': data.get('link_videochamada', ''),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    consultas = load_consultas()
    consultas.append(consulta)
    save_consultas(consultas)
    return jsonify(consulta), 201


@app.route('/api/medico/consultas/<consulta_id>', methods=['PUT'])
def medico_update_consulta(consulta_id):
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    consultas = load_consultas()
    idx = next((i for i, c in enumerate(consultas) if c.get('id') == consulta_id and c.get('medico_id') == mid), None)
    if idx is None:
        return jsonify({'error': 'not found'}), 404
    data = request.get_json(silent=True) or {}
    for k, v in data.items():
        if k not in ('id', 'medico_id', 'created_at'):
            consultas[idx][k] = v
    consultas[idx]['updated_at'] = datetime.now(timezone.utc).isoformat()
    save_consultas(consultas)
    return jsonify(consultas[idx])


@app.route('/api/medico/consultas/<consulta_id>', methods=['DELETE'])
def medico_delete_consulta(consulta_id):
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    consultas = load_consultas()
    consultas = [c for c in consultas if not (c.get('id') == consulta_id and c.get('medico_id') == mid)]
    save_consultas(consultas)
    return jsonify({'ok': True})


# --- Doctor Appointments (Agendamentos) ---
@app.route('/api/medico/agendamentos', methods=['GET'])
def medico_agendamentos():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    agendamentos = load_agendamentos()
    meus = [a for a in agendamentos if a.get('medico_id') == mid]
    return jsonify(meus)


@app.route('/api/medico/agendamentos', methods=['POST'])
def medico_criar_agendamento():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    data = request.get_json(silent=True) or {}
    agendamento = {
        'id': str(uuid.uuid4())[:8],
        'medico_id': mid,
        'paciente_id': data.get('paciente_id', ''),
        'paciente_nome': data.get('paciente_nome', ''),
        'data': data.get('data', ''),
        'hora': data.get('hora', ''),
        'tipo': data.get('tipo', 'videochamada'),
        'duracao': data.get('duracao', 30),
        'link_videochamada': data.get('link_videochamada', ''),
        'lembrete_enviado': False,
        'status': data.get('status', 'confirmado'),
        'notas': data.get('notas', ''),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    agendamentos = load_agendamentos()
    agendamentos.append(agendamento)
    save_agendamentos(agendamentos)
    return jsonify(agendamento), 201


@app.route('/api/medico/agendamentos/<ag_id>', methods=['PUT'])
def medico_update_agendamento(ag_id):
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    agendamentos = load_agendamentos()
    idx = next((i for i, a in enumerate(agendamentos) if a.get('id') == ag_id and a.get('medico_id') == mid), None)
    if idx is None:
        return jsonify({'error': 'not found'}), 404
    data = request.get_json(silent=True) or {}
    for k, v in data.items():
        if k not in ('id', 'medico_id', 'created_at'):
            agendamentos[idx][k] = v
    save_agendamentos(agendamentos)
    return jsonify(agendamentos[idx])


@app.route('/api/medico/agendamentos/<ag_id>', methods=['DELETE'])
def medico_delete_agendamento(ag_id):
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    agendamentos = load_agendamentos()
    agendamentos = [a for a in agendamentos if not (a.get('id') == ag_id and a.get('medico_id') == mid)]
    save_agendamentos(agendamentos)
    return jsonify({'ok': True})


# --- Doctor Patients (from leads) ---
@app.route('/api/medico/pacientes', methods=['GET'])
def medico_pacientes():
    """List patients associated with this doctor (from consultations)"""
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    consultas = load_consultas()
    # Get unique patient IDs from consultations
    paciente_ids = set()
    pacientes = []
    for c in consultas:
        if c.get('medico_id') == mid and c.get('paciente_id'):
            pid = c['paciente_id']
            if pid not in paciente_ids:
                paciente_ids.add(pid)
                pacientes.append({
                    'id': pid,
                    'nome': c.get('paciente_nome', ''),
                    'ultima_consulta': c.get('data', ''),
                    'total_consultas': sum(1 for cc in consultas if cc.get('medico_id') == mid and cc.get('paciente_id') == pid)
                })
    # Also include from leads
    leads = load_leads()
    for lead in leads:
        lid = lead.get('id', '')
        if lid and lid not in paciente_ids:
            if lead.get('medico_id') == mid:
                paciente_ids.add(lid)
                pacientes.append({
                    'id': lid,
                    'nome': lead.get('name', lead.get('nome', '')),
                    'email': lead.get('email', ''),
                    'telefone': lead.get('phone', lead.get('telefone', '')),
                    'ultima_consulta': '',
                    'total_consultas': 0
                })
    return jsonify(pacientes)


@app.route('/api/medico/pacientes/buscar', methods=['GET'])
def medico_buscar_pacientes():
    """Search patients by name or email"""
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    q = request.args.get('q', '').strip().lower()
    if not q:
        return jsonify([])
    leads = load_leads()
    results = []
    for lead in leads:
        name = (lead.get('name') or lead.get('nome') or '').lower()
        email = (lead.get('email') or '').lower()
        if q in name or q in email:
            results.append({
                'id': lead.get('id', ''),
                'nome': lead.get('name', lead.get('nome', '')),
                'email': lead.get('email', ''),
                'telefone': lead.get('phone', lead.get('telefone', ''))
            })
    return jsonify(results[:20])


# --- Doctor Platform Fee Config ---
TAXA_CONFIG_FILE = os.path.join(DATA_DIR, 'taxa_plataforma.json')

def load_taxa_config():
    if os.path.exists(TAXA_CONFIG_FILE):
        with open(TAXA_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'taxa_percentual': 15.0}

def save_taxa_config(data):
    with open(TAXA_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/api/medico/taxa', methods=['GET'])
def get_taxa():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    return jsonify(load_taxa_config())

@app.route('/api/medico/taxa', methods=['PUT'])
def set_taxa():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    data = request.get_json(silent=True) or {}
    taxa = float(data.get('taxa_percentual', 15.0))
    if taxa < 0 or taxa > 100:
        return jsonify({'message': 'Taxa deve ser entre 0 e 100.'}), 400
    config = load_taxa_config()
    config['taxa_percentual'] = taxa
    save_taxa_config(config)
    return jsonify(config)

# --- Doctor Financial Extract ---
@app.route('/api/medico/extrato', methods=['GET'])
def medico_extrato():
    """Financial extract for the logged doctor - with filters and payment status"""
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401

    # Query params
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    status_filter = request.args.get('status', '')  # concluida, agendada, todas

    taxa_config = load_taxa_config()
    taxa_pct = taxa_config.get('taxa_percentual', 15.0)
    fator_liquido = 1 - (taxa_pct / 100)

    consultas = load_consultas()
    agendamentos = load_agendamentos()

    # Filter consultas for this doctor
    minhas_consultas = [c for c in consultas if c.get('medico_id') == mid]
    minhas_agendamentos = [a for a in agendamentos if a.get('medico_id') == mid]

    # Build unified list of financial items
    items = []

    for c in minhas_consultas:
        data_consulta = c.get('data', '')
        # Apply date filters
        if data_inicio and data_consulta < data_inicio:
            continue
        if data_fim and data_consulta > data_fim:
            continue

        valor = float(c.get('valor', 0))
        status_c = c.get('status', 'pendente')

        # Determine payment status
        if status_c == 'concluida':
            pag_status = c.get('pagamento_status', 'pago')
        elif status_c == 'cancelada':
            pag_status = 'cancelado'
        else:
            pag_status = 'pendente'

        if status_filter and status_filter != 'todas':
            if status_filter == 'concluida' and status_c != 'concluida':
                continue
            if status_filter == 'agendada' and status_c not in ('agendada', 'confirmada', 'pendente'):
                continue
            if status_filter == 'pago' and pag_status != 'pago':
                continue
            if status_filter == 'a_receber' and pag_status not in ('pendente', 'a_receber'):
                continue

        items.append({
            'id': c.get('id', ''),
            'tipo': 'consulta',
            'data': data_consulta,
            'paciente': c.get('paciente_nome', c.get('paciente', '')),
            'descricao': c.get('tipo', 'Consulta'),
            'valor_bruto': valor,
            'valor_liquido': round(valor * fator_liquido, 2),
            'taxa_pct': taxa_pct,
            'status_consulta': status_c,
            'status_pagamento': pag_status
        })

    # Include agendamentos (future receivables)
    for a in minhas_agendamentos:
        data_ag = a.get('data', '')
        if data_inicio and data_ag < data_inicio:
            continue
        if data_fim and data_ag > data_fim:
            continue

        # Skip if already has a matching consulta
        ag_id = a.get('id', '')
        if any(i.get('id') == ag_id for i in items):
            continue

        valor = float(a.get('valor', 0))
        status_a = a.get('status', 'agendado')

        if status_filter and status_filter != 'todas':
            if status_filter == 'concluida':
                continue
            if status_filter == 'pago':
                continue

        items.append({
            'id': ag_id,
            'tipo': 'agendamento',
            'data': data_ag,
            'paciente': a.get('paciente_nome', a.get('paciente', '')),
            'descricao': a.get('tipo', 'Agendamento'),
            'valor_bruto': valor,
            'valor_liquido': round(valor * fator_liquido, 2),
            'taxa_pct': taxa_pct,
            'status_consulta': status_a,
            'status_pagamento': 'a_receber'
        })

    # Sort by date desc
    items.sort(key=lambda x: x.get('data', ''), reverse=True)

    # Calculate totals
    total_bruto = sum(i['valor_bruto'] for i in items)
    total_liquido = sum(i['valor_liquido'] for i in items)
    total_pago = sum(i['valor_liquido'] for i in items if i['status_pagamento'] == 'pago')
    total_pendente = sum(i['valor_liquido'] for i in items if i['status_pagamento'] == 'pendente')
    total_a_receber = sum(i['valor_liquido'] for i in items if i['status_pagamento'] == 'a_receber')
    total_cancelado = sum(i['valor_bruto'] for i in items if i['status_pagamento'] == 'cancelado')

    # Group by month
    meses = {}
    for i in items:
        mes_key = i['data'][:7] if i['data'] else 'sem-data'
        if mes_key not in meses:
            meses[mes_key] = {'mes': mes_key, 'consultas': 0, 'agendamentos': 0, 'valor_bruto': 0, 'valor_liquido': 0, 'pago': 0, 'pendente': 0, 'a_receber': 0}
        if i['tipo'] == 'consulta':
            meses[mes_key]['consultas'] += 1
        else:
            meses[mes_key]['agendamentos'] += 1
        meses[mes_key]['valor_bruto'] += i['valor_bruto']
        meses[mes_key]['valor_liquido'] += i['valor_liquido']
        if i['status_pagamento'] == 'pago':
            meses[mes_key]['pago'] += i['valor_liquido']
        elif i['status_pagamento'] == 'pendente':
            meses[mes_key]['pendente'] += i['valor_liquido']
        elif i['status_pagamento'] == 'a_receber':
            meses[mes_key]['a_receber'] += i['valor_liquido']

    meses_list = sorted(meses.values(), key=lambda x: x['mes'], reverse=True)

    return jsonify({
        'items': items,
        'total_items': len(items),
        'total_bruto': round(total_bruto, 2),
        'total_liquido': round(total_liquido, 2),
        'total_pago': round(total_pago, 2),
        'total_pendente': round(total_pendente, 2),
        'total_a_receber': round(total_a_receber, 2),
        'total_cancelado': round(total_cancelado, 2),
        'taxa_percentual': taxa_pct,
        'meses': meses_list
    })


# --- Doctor Evaluations ---
@app.route('/api/medico/avaliacoes', methods=['GET'])
def medico_avaliacoes():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    avaliacoes = load_avaliacoes()
    minhas = [a for a in avaliacoes if a.get('medico_id') == mid]
    media = 0
    if minhas:
        media = round(sum(a.get('nota', 0) for a in minhas) / len(minhas), 1)
    return jsonify({'avaliacoes': minhas, 'media': media, 'total': len(minhas)})


@app.route('/api/medico/avaliacoes', methods=['POST'])
def criar_avaliacao():
    """Patient submits evaluation for a doctor (no auth required)"""
    data = request.get_json(silent=True) or {}
    avaliacao = {
        'id': str(uuid.uuid4())[:8],
        'medico_id': data.get('medico_id', ''),
        'paciente_id': data.get('paciente_id', ''),
        'paciente_nome': data.get('paciente_nome', ''),
        'consulta_id': data.get('consulta_id', ''),
        'nota': min(5, max(1, int(data.get('nota', 5)))),
        'comentario': data.get('comentario', ''),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    avaliacoes = load_avaliacoes()
    avaliacoes.append(avaliacao)
    save_avaliacoes(avaliacoes)
    return jsonify(avaliacao), 201


# --- Doctor Dashboard Stats ---
@app.route('/api/medico/dashboard', methods=['GET'])
def medico_dashboard():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401

    consultas = load_consultas()
    agendamentos = load_agendamentos()
    avaliacoes = load_avaliacoes()

    minhas_consultas = [c for c in consultas if c.get('medico_id') == mid]
    meus_agendamentos = [a for a in agendamentos if a.get('medico_id') == mid]
    minhas_avaliacoes = [a for a in avaliacoes if a.get('medico_id') == mid]

    paciente_ids = set(c.get('paciente_id') for c in minhas_consultas if c.get('paciente_id'))
    concluidas = [c for c in minhas_consultas if c.get('status') == 'concluida']
    futuros = [a for a in meus_agendamentos if a.get('status') in ('confirmado', 'agendado')]
    media_aval = round(sum(a.get('nota', 0) for a in minhas_avaliacoes) / len(minhas_avaliacoes), 1) if minhas_avaliacoes else 0

    return jsonify({
        'total_pacientes': len(paciente_ids),
        'consultas_realizadas': len(concluidas),
        'avaliacao_media': media_aval,
        'proximos_agendamentos': len(futuros),
        'consultas_recentes': sorted(minhas_consultas, key=lambda c: c.get('created_at', ''), reverse=True)[:10],
        'agendamentos_futuros': sorted(futuros, key=lambda a: a.get('data', '') + a.get('hora', ''))[:10]
    })


# --- CID Search (ICD codes) ---
@app.route('/api/medico/cid/buscar', methods=['GET'])
def buscar_cid():
    """Search CID codes - local fallback, ready for WHO ICD API integration"""
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    q = request.args.get('q', '').strip().lower()
    if not q or len(q) < 2:
        return jsonify([])
    # Common CIDs as fallback
    cids_comuns = [
        {'codigo': 'F32', 'descricao': 'Episodio depressivo'},
        {'codigo': 'F41', 'descricao': 'Outros transtornos ansiosos'},
        {'codigo': 'G43', 'descricao': 'Enxaqueca'},
        {'codigo': 'G40', 'descricao': 'Epilepsia'},
        {'codigo': 'M54', 'descricao': 'Dorsalgia'},
        {'codigo': 'R52', 'descricao': 'Dor nao classificada em outra parte'},
        {'codigo': 'G25', 'descricao': 'Outros transtornos extrapiramidais e do movimento'},
        {'codigo': 'F90', 'descricao': 'Transtornos hipercineticos (TDAH)'},
        {'codigo': 'G35', 'descricao': 'Esclerose multipla'},
        {'codigo': 'C80', 'descricao': 'Neoplasia maligna sem especificacao de localizacao'},
        {'codigo': 'G47', 'descricao': 'Disturbios do sono'},
        {'codigo': 'F42', 'descricao': 'Transtorno obsessivo-compulsivo'},
        {'codigo': 'F31', 'descricao': 'Transtorno afetivo bipolar'},
        {'codigo': 'G20', 'descricao': 'Doenca de Parkinson'},
        {'codigo': 'F84', 'descricao': 'Transtornos globais do desenvolvimento (autismo)'},
        {'codigo': 'J45', 'descricao': 'Asma'},
        {'codigo': 'E10', 'descricao': 'Diabetes mellitus tipo 1'},
        {'codigo': 'E11', 'descricao': 'Diabetes mellitus tipo 2'},
        {'codigo': 'I10', 'descricao': 'Hipertensao essencial (primaria)'},
        {'codigo': 'K21', 'descricao': 'Doenca de refluxo gastroesofagico'},
    ]
    results = [c for c in cids_comuns if q in c['codigo'].lower() or q in c['descricao'].lower()]
    return jsonify(results[:20])


# --- Doctor Agenda (Horarios de Atendimento) ---
@app.route('/api/medico/agenda', methods=['GET'])
def medico_get_agenda():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    agendas = load_agenda_medica()
    minha = next((a for a in agendas if a.get('medico_id') == mid), None)
    if not minha:
        minha = {
            'medico_id': mid,
            'duracao_consulta': 30,
            'intervalo': 10,
            'antecedencia_min': 2,
            'antecedencia_max': 60,
            'horarios': {},
            'bloqueios': [],
            'integracao_calendario': {},
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
    return jsonify(minha)


@app.route('/api/medico/agenda', methods=['PUT'])
def medico_update_agenda():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    data = request.get_json(silent=True) or {}
    agendas = load_agenda_medica()
    minha = next((a for a in agendas if a.get('medico_id') == mid), None)
    if not minha:
        minha = {'medico_id': mid}
        agendas.append(minha)
    # Update fields
    if 'duracao_consulta' in data:
        minha['duracao_consulta'] = int(data['duracao_consulta'])
    if 'intervalo' in data:
        minha['intervalo'] = int(data['intervalo'])
    if 'antecedencia_min' in data:
        minha['antecedencia_min'] = int(data['antecedencia_min'])
    if 'antecedencia_max' in data:
        minha['antecedencia_max'] = int(data['antecedencia_max'])
    if 'horarios' in data:
        minha['horarios'] = data['horarios']
    if 'bloqueios' in data:
        minha['bloqueios'] = data['bloqueios']
    if 'integracao_calendario' in data:
        minha['integracao_calendario'] = data['integracao_calendario']
    minha['updated_at'] = datetime.now(timezone.utc).isoformat()
    save_agenda_medica(agendas)
    return jsonify(minha)


@app.route('/api/medico/agenda/bloqueio', methods=['POST'])
def medico_add_bloqueio():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    data = request.get_json(silent=True) or {}
    agendas = load_agenda_medica()
    minha = next((a for a in agendas if a.get('medico_id') == mid), None)
    if not minha:
        minha = {'medico_id': mid, 'horarios': {}, 'bloqueios': [], 'integracao_calendario': {}}
        agendas.append(minha)
    bloqueio = {
        'id': str(uuid.uuid4())[:8],
        'data_inicio': data.get('data_inicio', ''),
        'data_fim': data.get('data_fim', ''),
        'motivo': data.get('motivo', ''),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    if 'bloqueios' not in minha:
        minha['bloqueios'] = []
    minha['bloqueios'].append(bloqueio)
    minha['updated_at'] = datetime.now(timezone.utc).isoformat()
    save_agenda_medica(agendas)
    return jsonify(bloqueio), 201


@app.route('/api/medico/agenda/bloqueio/<bloqueio_id>', methods=['DELETE'])
def medico_delete_bloqueio(bloqueio_id):
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    agendas = load_agenda_medica()
    minha = next((a for a in agendas if a.get('medico_id') == mid), None)
    if not minha:
        return jsonify({'error': 'not found'}), 404
    minha['bloqueios'] = [b for b in minha.get('bloqueios', []) if b.get('id') != bloqueio_id]
    minha['updated_at'] = datetime.now(timezone.utc).isoformat()
    save_agenda_medica(agendas)
    return jsonify({'message': 'Bloqueio removido.'})


@app.route('/api/medico/agenda/integracao', methods=['PUT'])
def medico_update_integracao():
    mid = session.get('medico_id')
    if not mid:
        return jsonify({'message': 'Nao autenticado.'}), 401
    data = request.get_json(silent=True) or {}
    agendas = load_agenda_medica()
    minha = next((a for a in agendas if a.get('medico_id') == mid), None)
    if not minha:
        minha = {'medico_id': mid, 'horarios': {}, 'bloqueios': [], 'integracao_calendario': {}}
        agendas.append(minha)
    minha['integracao_calendario'] = data
    minha['updated_at'] = datetime.now(timezone.utc).isoformat()
    save_agenda_medica(agendas)
    return jsonify(minha['integracao_calendario'])


# --- Doctor Status Management (admin) ---
@app.route('/api/doctors/<doc_id>/aprovar', methods=['POST'])
def aprovar_medico(doc_id):
    """Admin approves a doctor registration"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Nao autenticado como admin.'}), 401
    docs = load_doctors()
    doc = next((d for d in docs if d.get('id') == doc_id), None)
    if not doc:
        return jsonify({'error': 'not found'}), 404
    doc['status'] = 'aprovado'
    doc['approved_at'] = datetime.now(timezone.utc).isoformat()
    save_doctors(docs)
    return jsonify(doc)


@app.route('/api/doctors/<doc_id>/rejeitar', methods=['POST'])
def rejeitar_medico(doc_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Nao autenticado como admin.'}), 401
    docs = load_doctors()
    doc = next((d for d in docs if d.get('id') == doc_id), None)
    if not doc:
        return jsonify({'error': 'not found'}), 404
    doc['status'] = 'rejeitado'
    save_doctors(docs)
    return jsonify(doc)


# ===== GESTAO DE PACIENTES API =====

# --- Kanban Pacientes - Constants ---
KANBAN_ETAPAS = [
    'formulario_anamnese', 'consultas', 'solicitacao_teste',
    'retorno_resultado', 'orcamento_prescricao', 'documentacao_anvisa',
    'medicamento_exportacao', 'acompanhamento_45'
]

@app.route('/api/pacientes', methods=['GET'])
def list_pacientes():
    """List all patients"""
    pacientes = load_pacientes()
    status_filter = request.args.get('status', '')
    if status_filter:
        pacientes = [p for p in pacientes if p.get('status') == status_filter]
    return jsonify(pacientes)

# --- Stats (must be before <pac_id> route) ---
@app.route('/api/pacientes/stats', methods=['GET'])
def pacientes_stats():
    pacientes = load_pacientes()
    total = len(pacientes)
    ativos = sum(1 for p in pacientes if p.get('status') == 'ativo')
    pendentes_anamnese = sum(1 for p in pacientes if not p.get('anamnese_preenchida'))
    pendentes_docs = sum(1 for p in pacientes if not p.get('documentos_enviados'))
    kanban_cols = {
        'formulario_anamnese': 0, 'consultas': 0, 'solicitacao_teste': 0,
        'retorno_resultado': 0, 'orcamento_prescricao': 0, 'documentacao_anvisa': 0,
        'medicamento_exportacao': 0, 'acompanhamento_45': 0
    }
    for p in pacientes:
        etapa = p.get('kanban_etapa', 'formulario_anamnese')
        if etapa in kanban_cols:
            kanban_cols[etapa] += 1
    return jsonify({
        'total': total,
        'ativos': ativos,
        'pendentes_anamnese': pendentes_anamnese,
        'pendentes_docs': pendentes_docs,
        'kanban': kanban_cols
    })

# --- Kanban board (must be before <pac_id> route) ---
@app.route('/api/pacientes/kanban', methods=['GET'])
def get_kanban_pacientes():
    """Return patients grouped by kanban column"""
    pacientes = load_pacientes()
    board = {etapa: [] for etapa in KANBAN_ETAPAS}
    for p in pacientes:
        etapa = p.get('kanban_etapa', 'formulario_anamnese')
        if etapa not in board:
            etapa = 'formulario_anamnese'
        board[etapa].append(p)
    return jsonify(board)

# --- Converter Lead (must be before <pac_id> route) ---
@app.route('/api/pacientes/converter-lead', methods=['POST'])
def converter_lead_route():
    data = request.get_json(silent=True) or {}
    lead_id = data.get('lead_id')
    if not lead_id:
        return jsonify({'error': 'lead_id obrigatorio'}), 400
    pac = converter_lead_para_paciente(lead_id)
    if not pac:
        return jsonify({'error': 'Lead nao encontrado ou ja convertido'}), 400
    return jsonify(pac), 201

@app.route('/api/pacientes/<pac_id>', methods=['GET'])
def get_paciente(pac_id):
    """Get patient details"""
    pacientes = load_pacientes()
    pac = next((p for p in pacientes if p.get('id') == pac_id), None)
    if not pac:
        return jsonify({'error': 'Paciente nao encontrado'}), 404
    return jsonify(pac)

@app.route('/api/pacientes', methods=['POST'])
def create_paciente():
    """Create a new patient manually or from lead conversion"""
    data = request.get_json(silent=True) or {}
    
    # If lead_id provided, convert lead
    lead_id = data.get('lead_id')
    if lead_id:
        pac = converter_lead_para_paciente(lead_id)
        if pac:
            return jsonify(pac), 201
        return jsonify({'error': 'Lead nao encontrado ou ja convertido'}), 400
    
    pacientes = load_pacientes()
    pac_id = get_next_paciente_id()
    import secrets
    token = secrets.token_urlsafe(32)
    
    paciente = {
        'id': pac_id,
        'lead_id': '',
        'nome': data.get('nome', ''),
        'cpf': data.get('cpf', ''),
        'data_nascimento': data.get('data_nascimento', ''),
        'sexo': data.get('sexo', ''),
        'idade': data.get('idade', ''),
        'foto_url': data.get('foto_url', ''),
        'convenio': data.get('convenio', ''),
        'email': data.get('email', ''),
        'telefone': data.get('telefone', ''),
        'endereco': data.get('endereco', ''),
        'responsavel_nome': data.get('responsavel_nome', ''),
        'responsavel_cpf': data.get('responsavel_cpf', ''),
        'diagnostico_atual': data.get('diagnostico_atual', ''),
        'medico_responsavel_id': data.get('medico_responsavel_id', ''),
        'medico_responsavel_nome': data.get('medico_responsavel_nome', ''),
        'status': 'ativo',
        'kanban_etapa': 'formulario_anamnese',
        'pagamento_confirmado': data.get('pagamento_confirmado', False),
        'anamnese_preenchida': False,
        'documentos_enviados': False,
        'cadastro_completo': False,
        'token_acesso': token,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    pacientes.append(paciente)
    save_pacientes(pacientes)
    add_timeline_event(pac_id, 'cadastro', 'Paciente cadastrado', 'Cadastro manual realizado')
    return jsonify(paciente), 201

@app.route('/api/pacientes/<pac_id>', methods=['PUT'])
def update_paciente(pac_id):
    """Update patient data"""
    pacientes = load_pacientes()
    idx = next((i for i, p in enumerate(pacientes) if p.get('id') == pac_id), None)
    if idx is None:
        return jsonify({'error': 'Paciente nao encontrado'}), 404
    data = request.get_json(silent=True) or {}
    for k, v in data.items():
        if k not in ['id', 'created_at', 'token_acesso']:
            pacientes[idx][k] = v
    pacientes[idx]['updated_at'] = datetime.now(timezone.utc).isoformat()
    save_pacientes(pacientes)
    return jsonify(pacientes[idx])

@app.route('/api/pacientes/<pac_id>', methods=['DELETE'])
def delete_paciente(pac_id):
    pacientes = load_pacientes()
    pacientes = [p for p in pacientes if p.get('id') != pac_id]
    save_pacientes(pacientes)
    return jsonify({'ok': True})

@app.route('/api/pacientes/<pac_id>/foto', methods=['POST'])
def upload_foto_paciente(pac_id):
    """Upload patient photo"""
    pacientes = load_pacientes()
    pac = next((p for p in pacientes if p.get('id') == pac_id), None)
    if not pac:
        return jsonify({'error': 'Paciente nao encontrado'}), 404
    if 'foto' not in request.files:
        return jsonify({'error': 'Nenhuma foto enviada'}), 400
    foto = request.files['foto']
    if foto and foto.filename:
        filename = secure_filename(foto.filename)
        target_dir = os.path.join(UPLOADS_DIR, pac_id)
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, filename)
        foto.save(path)
        pac['foto_url'] = '/uploads/' + pac_id + '/' + filename
        pac['updated_at'] = datetime.now(timezone.utc).isoformat()
        save_pacientes(pacientes)
    return jsonify(pac)

# --- Timeline do Paciente ---
@app.route('/api/pacientes/<pac_id>/timeline', methods=['GET'])
def get_timeline_paciente(pac_id):
    """Get patient timeline events"""
    tl = load_timeline()
    events = [e for e in tl if e.get('paciente_id') == pac_id]
    events.sort(key=lambda x: x.get('data', ''), reverse=True)
    return jsonify(events)

@app.route('/api/pacientes/<pac_id>/timeline', methods=['POST'])
def add_timeline_paciente(pac_id):
    """Add a timeline event for a patient"""
    data = request.get_json(silent=True) or {}
    event = add_timeline_event(
        pac_id,
        data.get('tipo', 'nota'),
        data.get('titulo', 'Evento'),
        data.get('descricao', ''),
        data.get('dados', {})
    )
    return jsonify(event), 201

@app.route('/api/pacientes/<pac_id>/timeline/<event_id>', methods=['DELETE'])
def delete_timeline_event(pac_id, event_id):
    """Delete a timeline event"""
    tl = load_timeline()
    tl = [e for e in tl if not (e.get('id') == event_id and e.get('paciente_id') == pac_id)]
    save_timeline(tl)
    return jsonify({'status': 'ok'})

# --- Ficha de Atendimento ---
@app.route('/api/pacientes/<pac_id>/ficha', methods=['GET'])
def get_ficha(pac_id):
    """Get ficha de atendimento for a patient"""
    fichas = load_fichas()
    ficha = fichas.get(pac_id, {})
    return jsonify(ficha)

@app.route('/api/pacientes/<pac_id>/ficha', methods=['POST'])
def save_ficha(pac_id):
    """Save/update ficha de atendimento for a patient"""
    data = request.get_json()
    fichas = load_fichas()
    existing = fichas.get(pac_id, {})
    existing_evolucoes = existing.get('evolucoes', [])
    fichas[pac_id] = {
        'queixa_principal': data.get('queixa_principal', ''),
        'hda': data.get('hda', ''),
        'doencas_previas': data.get('doencas_previas', ''),
        'historico_familiar': data.get('historico_familiar', ''),
        'alergias': data.get('alergias', ''),
        'medicacoes': data.get('medicacoes', ''),
        'cirurgias': data.get('cirurgias', ''),
        'habitos': data.get('habitos', ''),
        'exame_fisico': data.get('exame_fisico', ''),
        'diagnostico': data.get('diagnostico', ''),
        'estadiamento': data.get('estadiamento', ''),
        'conduta': data.get('conduta', ''),
        'observacoes': data.get('observacoes', ''),
        'evolucoes': existing_evolucoes,
        'atualizado_em': datetime.now().isoformat()
    }
    save_fichas(fichas)
    return jsonify({'success': True, 'message': 'Ficha salva com sucesso'})

@app.route('/api/pacientes/<pac_id>/ficha/evolucao', methods=['POST'])
def add_evolucao(pac_id):
    """Add an evolution note to the ficha"""
    data = request.get_json()
    texto = data.get('texto', '').strip()
    if not texto:
        return jsonify({'error': 'Texto obrigatório'}), 400
    fichas = load_fichas()
    ficha = fichas.get(pac_id, {})
    evolucoes = ficha.get('evolucoes', [])
    import uuid
    evolucoes.append({
        'id': str(uuid.uuid4())[:8],
        'texto': texto,
        'data': datetime.now().isoformat()
    })
    ficha['evolucoes'] = evolucoes
    fichas[pac_id] = ficha
    save_fichas(fichas)
    return jsonify({'success': True, 'evolucoes': evolucoes})

@app.route('/api/pacientes/<pac_id>/ficha/evolucao/<evol_id>', methods=['DELETE'])
def delete_evolucao(pac_id, evol_id):
    """Delete an evolution note"""
    fichas = load_fichas()
    ficha = fichas.get(pac_id, {})
    evolucoes = ficha.get('evolucoes', [])
    ficha['evolucoes'] = [e for e in evolucoes if e.get('id') != evol_id]
    fichas[pac_id] = ficha
    save_fichas(fichas)
    return jsonify({'success': True, 'evolucoes': ficha['evolucoes']})

# --- Prontuario Eletronico ---
@app.route('/api/pacientes/<pac_id>/prontuario', methods=['GET'])
def get_prontuario(pac_id):
    """Get all medical records for a patient"""
    prontuarios = load_prontuarios()
    records = [p for p in prontuarios if p.get('paciente_id') == pac_id]
    # Separate by type
    result = {
        'exames': [r for r in records if r.get('tipo') == 'exame'],
        'receituario': [r for r in records if r.get('tipo') == 'receituario'],
        'laudos': [r for r in records if r.get('tipo') == 'laudo'],
        'anexos': [r for r in records if r.get('tipo') == 'anexo']
    }
    return jsonify(result)

@app.route('/api/pacientes/<pac_id>/prontuario', methods=['POST'])
def add_prontuario(pac_id):
    """Add a record to patient prontuario"""
    prontuarios = load_prontuarios()
    data = request.get_json(silent=True) or {}
    record = {
        'id': f'PRON{len(prontuarios)+1:05d}',
        'paciente_id': pac_id,
        'tipo': data.get('tipo', 'anexo'),  # exame, receituario, laudo, anexo
        'titulo': data.get('titulo', ''),
        'descricao': data.get('descricao', ''),
        'conteudo': data.get('conteudo', ''),
        'arquivo_url': data.get('arquivo_url', ''),
        'medico_id': data.get('medico_id', ''),
        'medico_nome': data.get('medico_nome', ''),
        'data': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    prontuarios.append(record)
    save_prontuarios(prontuarios)
    
    tipo_labels = {'exame': 'Exame adicionado', 'receituario': 'Receituario adicionado',
                   'laudo': 'Laudo adicionado', 'anexo': 'Anexo adicionado'}
    add_timeline_event(pac_id, 'prontuario', tipo_labels.get(record['tipo'], 'Registro adicionado'),
                       record['titulo'])
    return jsonify(record), 201

@app.route('/api/pacientes/<pac_id>/prontuario/upload', methods=['POST'])
def upload_prontuario(pac_id):
    """Upload a file to patient prontuario"""
    if 'arquivo' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    arquivo = request.files['arquivo']
    tipo = request.form.get('tipo', 'anexo')
    titulo = request.form.get('titulo', arquivo.filename)
    descricao = request.form.get('descricao', '')
    
    if arquivo and arquivo.filename:
        filename = secure_filename(arquivo.filename)
        target_dir = os.path.join(UPLOADS_DIR, pac_id, 'prontuario')
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, filename)
        arquivo.save(path)
        arquivo_url = f'/uploads/{pac_id}/prontuario/{filename}'
        
        prontuarios = load_prontuarios()
        record = {
            'id': f'PRON{len(prontuarios)+1:05d}',
            'paciente_id': pac_id,
            'tipo': tipo,
            'titulo': titulo,
            'descricao': descricao,
            'conteudo': '',
            'arquivo_url': arquivo_url,
            'medico_id': request.form.get('medico_id', ''),
            'medico_nome': request.form.get('medico_nome', ''),
            'data': datetime.now(timezone.utc).isoformat(),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        prontuarios.append(record)
        save_prontuarios(prontuarios)
        add_timeline_event(pac_id, 'upload', f'Arquivo enviado: {titulo}', descricao)
        return jsonify(record), 201
    return jsonify({'error': 'Arquivo invalido'}), 400

# --- Links automaticos do paciente ---
@app.route('/api/pacientes/<pac_id>/links', methods=['GET'])
def get_paciente_links(pac_id):
    """Generate automatic links for the patient"""
    pacientes = load_pacientes()
    pac = next((p for p in pacientes if p.get('id') == pac_id), None)
    if not pac:
        return jsonify({'error': 'Paciente nao encontrado'}), 404
    
    token = pac.get('token_acesso', '')
    base = request.host_url.rstrip('/')
    
    links = {
        'acesso_plataforma': f'{base}/paciente?token={token}',
        'anamnese': f'{base}/paciente/anamnese?token={token}',
        'documentos': f'{base}/paciente/documentos?token={token}',
        'cadastro': f'{base}/?registerPaciente=true&token={token}'
    }
    return jsonify(links)

# --- Kanban Mover (keep here, uses <pac_id>) ---
@app.route('/api/pacientes/<pac_id>/kanban-mover', methods=['PUT'])
def mover_paciente_kanban(pac_id):
    """Move patient to a different kanban column (manual or auto)"""
    pacientes = load_pacientes()
    idx = next((i for i, p in enumerate(pacientes) if p.get('id') == pac_id), None)
    if idx is None:
        return jsonify({'error': 'Paciente nao encontrado'}), 404
    data = request.get_json(silent=True) or {}
    nova_etapa = data.get('etapa', '')
    if nova_etapa not in KANBAN_ETAPAS:
        return jsonify({'error': f'Etapa invalida: {nova_etapa}'}), 400
    etapa_anterior = pacientes[idx].get('kanban_etapa', 'formulario_anamnese')
    pacientes[idx]['kanban_etapa'] = nova_etapa
    pacientes[idx]['updated_at'] = datetime.now(timezone.utc).isoformat()
    save_pacientes(pacientes)
    etapa_labels = {
        'formulario_anamnese': 'Formulário/Anamnese',
        'consultas': 'Consultas',
        'solicitacao_teste': 'Solicitação de Teste Genético',
        'retorno_resultado': 'Retorno/Resultado do Teste',
        'orcamento_prescricao': 'Orçamento Prescrição Cannabis',
        'documentacao_anvisa': 'Documentação Anvisa',
        'medicamento_exportacao': 'Medicamento em Exportação',
        'acompanhamento_45': 'Acompanhamento Paciente (45 dias)'
    }
    add_timeline_event(pac_id, 'evolucao', 'Movimentação no Kanban',
        f'Paciente movido de "{etapa_labels.get(etapa_anterior, etapa_anterior)}" para "{etapa_labels.get(nova_etapa, nova_etapa)}"')
    return jsonify(pacientes[idx])


# ===== PRESCRIÇÃO MÉDICA API =====
@app.route('/api/pacientes/<pac_id>/prescricao', methods=['POST'])
def criar_prescricao(pac_id):
    """Create a new prescription for a patient and auto-save to prontuário"""
    pacientes = load_pacientes()
    pac = next((p for p in pacientes if p.get('id') == pac_id), None)
    if not pac:
        return jsonify({'error': 'Paciente não encontrado'}), 404

    data = request.get_json(silent=True) or {}
    medicamentos_prescritos = data.get('medicamentos', [])
    observacoes = data.get('observacoes', '')
    medico_id = data.get('medico_id', '')
    medico_nome = data.get('medico_nome', '')
    medico_crm = data.get('medico_crm', '')
    duracao_meses = data.get('duracao_meses', 24)
    signature_provider = data.get('signature_provider', 'vidaas')

    if not medicamentos_prescritos:
        return jsonify({'error': 'Nenhum medicamento selecionado'}), 400

    # Generate prescription ID
    prescricoes = load_prescricoes()
    presc_id = f'PRESC{len(prescricoes)+1:05d}'

    # Build structured content for renderDocReceituario parser
    conteudo_lines = []
    for med in medicamentos_prescritos:
        conteudo_lines.append(f"MEDICAMENTO: {med.get('nome', '')}")
        if med.get('dosagem'):
            conteudo_lines.append(f"Dosagem: {med['dosagem']}")
        if med.get('posologia'):
            conteudo_lines.append(f"Posologia: {med['posologia']}")
        if med.get('quantidade'):
            conteudo_lines.append(f"Quantidade: {med['quantidade']}")
        if med.get('duracao'):
            conteudo_lines.append(f"Duração: {med['duracao']}")
        conteudo_lines.append('')

    if observacoes:
        conteudo_lines.append(f"OBSERVAÇÕES: {observacoes}")

    conteudo_lines.append(f"{medico_nome}")
    conteudo_lines.append(f"{medico_crm}")

    conteudo = '\n'.join(conteudo_lines)

    # Save prescription record
    prescricao = {
        'id': presc_id,
        'paciente_id': pac_id,
        'paciente_nome': pac.get('nome', ''),
        'medicamentos': medicamentos_prescritos,
        'observacoes': observacoes,
        'medico_id': medico_id,
        'medico_nome': medico_nome,
        'medico_crm': medico_crm,
        'duracao_meses': duracao_meses,
        'signature_provider': signature_provider,
        'is_signed': True,
        'signature_hash': '',
        'status': 'assinada',
        'data': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    prescricoes.append(prescricao)
    save_prescricoes(prescricoes)

    # Auto-save to prontuário as receituário
    prontuarios = load_prontuarios()
    titulo = f"Prescrição Cannabis - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    descricao_items = [med.get('nome', '') for med in medicamentos_prescritos]
    pron_record = {
        'id': f'PRON{len(prontuarios)+1:05d}',
        'paciente_id': pac_id,
        'tipo': 'receituario',
        'titulo': titulo,
        'descricao': ', '.join(descricao_items),
        'conteudo': conteudo,
        'arquivo_url': '',
        'medico_id': medico_id,
        'medico_nome': medico_nome,
        'data': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    prontuarios.append(pron_record)
    save_prontuarios(prontuarios)

    # Add timeline event
    add_timeline_event(pac_id, 'prescricao', 'Prescrição médica realizada',
        f'{medico_nome} prescreveu: {", ".join(descricao_items)}')

    # Fire webhook notification to commercial team
    try:
        wh_config = load_webhooks_config()
        if wh_config.get('prescricao_ativo') and wh_config.get('prescricao_url'):
            import requests as req
            webhook_payload = {
                'evento': 'nova_prescricao',
                'prescricao_id': presc_id,
                'paciente_id': pac_id,
                'paciente_nome': pac.get('nome', ''),
                'paciente_email': pac.get('email', ''),
                'paciente_telefone': pac.get('telefone', ''),
                'medicamentos': medicamentos_prescritos,
                'medico_nome': medico_nome,
                'medico_crm': medico_crm,
                'observacoes': observacoes,
                'data': datetime.now(timezone.utc).isoformat(),
                'mensagem': f'Nova prescrição de cannabis realizada para {pac.get("nome", "")}. Paciente aguardando orçamento de medicamento.'
            }
            req.post(
                wh_config['prescricao_url'],
                json=webhook_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            logger.info(f"✅ Webhook de prescrição enviado para {wh_config['prescricao_url']}")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar webhook de prescrição: {e}")

    return jsonify({
        'prescricao': prescricao,
        'prontuario': pron_record,
        'message': 'Prescrição assinada e salva no receituário com sucesso'
    }), 201


@app.route('/api/pacientes/<pac_id>/prescricoes', methods=['GET'])
def listar_prescricoes(pac_id):
    """List all prescriptions for a patient"""
    prescricoes = load_prescricoes()
    pac_prescricoes = [p for p in prescricoes if p.get('paciente_id') == pac_id]
    pac_prescricoes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(pac_prescricoes)


# ===== CANNABIS CALCULATOR API =====
import math

@app.route('/api/cannabis/calcular', methods=['POST'])
def calcular_cannabis():
    """Cannabis titration calculator - calculates bottles needed for 24 months"""
    data = request.get_json(silent=True) or {}
    produto_id = data.get('produto_id', '')
    titration_plan = data.get('titration_plan', [])
    duration_months = data.get('duration_months', 24)

    medicamentos = load_medicamentos()
    produto = next((m for m in medicamentos if m.get('id') == produto_id), None)
    if not produto:
        return jsonify({'error': 'Produto não encontrado'}), 404

    volume_ml = float(produto.get('volume_ml', 0) or 0)
    drops_per_ml = int(produto.get('drops_per_ml', 20) or 20)
    concentration_mg_ml = float(produto.get('concentration_mg_ml', 0) or 0)

    if volume_ml <= 0:
        import re
        vol_str = produto.get('volume', '')
        vol_match = re.search(r'(\d+)\s*ml', vol_str, re.IGNORECASE)
        volume_ml = float(vol_match.group(1)) if vol_match else 30

    total_drops_needed = 0
    days_covered = 0

    for step in titration_plan:
        daily_drops = int(step.get('morning', 0)) + int(step.get('afternoon', 0)) + int(step.get('night', 0))
        period = step.get('period', '')

        if period.lower().startswith('manuten'):
            total_days = duration_months * 30
            remaining_days = total_days - days_covered
            if remaining_days > 0:
                total_drops_needed += daily_drops * remaining_days
                days_covered = total_days
        else:
            step_days = int(step.get('days', 7))
            total_drops_needed += daily_drops * step_days
            days_covered += step_days

    drops_per_bottle = volume_ml * drops_per_ml
    if drops_per_bottle <= 0:
        drops_per_bottle = 600

    bottles_needed = math.ceil(total_drops_needed / drops_per_bottle)
    bottles_with_margin = math.ceil(bottles_needed * 1.10)
    mg_per_drop = concentration_mg_ml / drops_per_ml if drops_per_ml > 0 and concentration_mg_ml > 0 else 0

    return jsonify({
        'total_drops': total_drops_needed,
        'drops_per_bottle': int(drops_per_bottle),
        'bottles_needed': bottles_needed,
        'bottles_with_margin': bottles_with_margin,
        'days_covered': days_covered,
        'duration_months': duration_months,
        'mg_per_drop': round(mg_per_drop, 2),
        'volume_ml': volume_ml,
        'product_name': produto.get('nome', '')
    })


# ===== FORNECEDORES API =====
@app.route('/api/fornecedores', methods=['GET'])
def list_fornecedores():
    return jsonify(load_fornecedores())

@app.route('/api/fornecedores', methods=['POST'])
def create_fornecedor():
    fornecedores = load_fornecedores()
    data = request.get_json(silent=True) or {}
    fornecedor = {
        'id': f'FORN{len(fornecedores)+1:04d}',
        'nome': data.get('nome', ''),
        'cnpj': data.get('cnpj', ''),
        'pais': data.get('pais', ''),
        'contato': data.get('contato', ''),
        'email': data.get('email', ''),
        'telefone': data.get('telefone', ''),
        'marcas': data.get('marcas', []),
        'observacoes': data.get('observacoes', ''),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    fornecedores.append(fornecedor)
    save_fornecedores(fornecedores)
    return jsonify(fornecedor), 201

@app.route('/api/fornecedores/<forn_id>', methods=['PUT'])
def update_fornecedor(forn_id):
    fornecedores = load_fornecedores()
    idx = next((i for i, f in enumerate(fornecedores) if f.get('id') == forn_id), None)
    if idx is None:
        return jsonify({'error': 'not found'}), 404
    data = request.get_json(silent=True) or {}
    for k, v in data.items():
        if k != 'id':
            fornecedores[idx][k] = v
    save_fornecedores(fornecedores)
    return jsonify(fornecedores[idx])

@app.route('/api/fornecedores/<forn_id>', methods=['DELETE'])
def delete_fornecedor(forn_id):
    fornecedores = load_fornecedores()
    fornecedores = [f for f in fornecedores if f.get('id') != forn_id]
    save_fornecedores(fornecedores)
    return jsonify({'ok': True})


# ===== LAUDO MÉDICO API =====
@app.route('/api/pacientes/<pac_id>/laudo', methods=['POST'])
def criar_laudo(pac_id):
    """Create a medical report (Laudo Médico Circunstanciado) for judicial process"""
    pacientes = load_pacientes()
    pac = next((p for p in pacientes if p.get('id') == pac_id), None)
    if not pac:
        return jsonify({'error': 'Paciente não encontrado'}), 404

    data = request.get_json(silent=True) or {}
    laudos = load_laudos()
    laudo_id = f'LAUDO{len(laudos)+1:05d}'

    laudo = {
        'id': laudo_id,
        'paciente_id': pac_id,
        'paciente_nome': pac.get('nome', ''),
        'diagnostico_cid': data.get('diagnostico_cid', ''),
        'historico_clinico': data.get('historico_clinico', ''),
        'tratamentos_anteriores': data.get('tratamentos_anteriores', ''),
        'medicacoes_atuais': data.get('medicacoes_atuais', ''),
        'justificativa_cannabis': data.get('justificativa_cannabis', ''),
        'consequencias_negativa': data.get('consequencias_negativa', ''),
        'hipossuficiencia': data.get('hipossuficiencia', ''),
        'conclusao': data.get('conclusao', ''),
        'medico_nome': data.get('medico_nome', ''),
        'medico_crm': data.get('medico_crm', ''),
        'signature_provider': data.get('signature_provider', 'vidaas'),
        'is_signed': False,
        'signature_hash': '',
        'status': 'rascunho',
        'data': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    laudos.append(laudo)
    save_laudos(laudos)

    prontuarios = load_prontuarios()
    titulo = f"Laudo Médico Circunstanciado - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    conteudo_lines = [
        "LAUDO MÉDICO CIRCUNSTANCIADO", "",
        f"PACIENTE: {pac.get('nome', '')}", f"CPF: {pac.get('cpf', '')}",
        f"DIAGNÓSTICO (CID): {laudo['diagnostico_cid']}", "",
        "1. HISTÓRICO CLÍNICO (ANAMNESE):", laudo['historico_clinico'], "",
        "2. TRATAMENTOS ANTERIORES (FALHA TERAPÊUTICA):", laudo['tratamentos_anteriores'], "",
        "3. MEDICAÇÕES ATUAIS:", laudo['medicacoes_atuais'], "",
        "4. JUSTIFICATIVA PARA USO DE CANNABIS MEDICINAL:", laudo['justificativa_cannabis'], "",
        "5. CONSEQUÊNCIAS DA AUSÊNCIA DE TRATAMENTO:", laudo['consequencias_negativa'], "",
        "6. HIPOSSUFICIÊNCIA E JUSTIFICATIVA FINANCEIRA:", laudo['hipossuficiencia'], "",
        "CONCLUSÃO:", laudo['conclusao'], "",
        laudo['medico_nome'], laudo['medico_crm']
    ]
    pron_record = {
        'id': f'PRON{len(prontuarios)+1:05d}',
        'paciente_id': pac_id,
        'tipo': 'laudo',
        'titulo': titulo,
        'descricao': f"CID: {laudo['diagnostico_cid']}",
        'conteudo': '\n'.join(conteudo_lines),
        'arquivo_url': '',
        'medico_id': '',
        'medico_nome': laudo['medico_nome'],
        'data': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    prontuarios.append(pron_record)
    save_prontuarios(prontuarios)

    add_timeline_event(pac_id, 'laudo', 'Laudo Médico Circunstanciado gerado',
        f'{laudo["medico_nome"]} emitiu laudo - CID: {laudo["diagnostico_cid"]}')

    return jsonify({
        'laudo': laudo, 'prontuario': pron_record,
        'message': 'Laudo gerado e salvo no prontuário'
    }), 201


@app.route('/api/pacientes/<pac_id>/laudos', methods=['GET'])
def listar_laudos(pac_id):
    laudos = load_laudos()
    pac_laudos = [l for l in laudos if l.get('paciente_id') == pac_id]
    pac_laudos.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(pac_laudos)


# ===== ASSINATURA DIGITAL API (IntegraICP) =====
ASSINATURAS_FILE = os.path.join(DATA_DIR, 'assinaturas.json')

def load_assinaturas():
    return _load_json_file(ASSINATURAS_FILE, [])

def save_assinaturas(data):
    _save_json_file(ASSINATURAS_FILE, data)

try:
    from integraicp_service import IntegraICPService
    integraicp = IntegraICPService()
    if integraicp.is_configured():
        logger.info("✅ IntegraICP configurado — assinatura digital real habilitada")
    else:
        logger.warning("⚠️ IntegraICP sem channel_id — modo simulado ativo")
except ImportError:
    integraicp = None
    logger.warning("⚠️ integraicp_service.py não encontrado — modo simulado ativo")


@app.route('/api/assinatura/iniciar', methods=['POST'])
def iniciar_assinatura():
    """
    Inicia o fluxo de assinatura digital conforme diagrama IntegraICP:
    1. Server chama GET /authentications → lista de Clearances
    2. Retorna clearances ao frontend para seleção do provedor
    3. Usuário seleciona → browser abre clearanceEndpoint → 302 → auth no provedor
    Se IntegraICP não configurado, assina em modo simulado.
    """
    data = request.get_json(silent=True) or {}
    doc_type = data.get('doc_type', '')
    doc_id = data.get('doc_id', '')
    provider = data.get('provider', 'integraicp')
    medico_nome = data.get('medico_nome', '')
    medico_crm = data.get('medico_crm', '')
    medico_cpf = data.get('medico_cpf', '')

    import hashlib
    hash_content = f"{doc_type}:{doc_id}:{medico_nome}:{medico_crm}:{datetime.now(timezone.utc).isoformat()}"
    doc_hash = hashlib.sha256(hash_content.encode()).hexdigest()

    # ── Modo IntegraICP (real) ──
    if integraicp and integraicp.is_configured() and provider == 'integraicp':
        pkce = integraicp.generate_pkce_pair()
        session_id = uuid.uuid4().hex[:12]

        callback_uri = integraicp.build_callback_uri(doc_type, doc_id, session_id)

        # Passo 1 do diagrama: GET /authentications → lista de Clearances (server-side)
        try:
            clearances_result = integraicp.get_clearances(
                code_challenge=pkce['code_challenge'],
                callback_uri=callback_uri,
                subject_key=medico_cpf if medico_cpf else None,
                credential_lifetime=3600
            )
        except Exception as e:
            logger.error(f"Erro ao consultar IntegraICP /authentications: {e}")
            return jsonify({'error': f'Erro ao consultar provedores ICP-Brasil: {str(e)}'}), 502

        # Verificar erros da API
        if 'error' in clearances_result and 'data' not in clearances_result:
            return jsonify({
                'mode': 'integraicp',
                'error': 'Erro ao consultar provedores ICP-Brasil',
                'detail': clearances_result.get('error', {}),
                'status_code': clearances_result.get('status_code', 400)
            }), 400

        # HTTP 302 → autostart ativado, retorna URL de redirect direto
        if clearances_result.get('redirect'):
            # Salvar sessão antes do redirect
            sig_session = {
                'id': f'SIG{uuid.uuid4().hex[:8].upper()}',
                'session_id': session_id,
                'doc_type': doc_type,
                'doc_id': doc_id,
                'medico_nome': medico_nome,
                'medico_crm': medico_crm,
                'medico_cpf': medico_cpf,
                'doc_hash': doc_hash,
                'code_verifier': pkce['code_verifier'],
                'code_challenge': pkce['code_challenge'],
                'status': 'pending_authentication',
                'credential_id': None,
                'signature_data': None,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            sigs = load_assinaturas()
            sigs.append(sig_session)
            save_assinaturas(sigs)

            return jsonify({
                'mode': 'integraicp',
                'session_id': session_id,
                'redirect_url': clearances_result['redirect_url'],
                'message': 'Redirecionando para autenticação'
            })

        # Extrair clearances da resposta
        data_obj = clearances_result.get('data', {})
        clearances = data_obj.get('clearances', [])
        exec_status = data_obj.get('executionStatus', {})

        if not clearances or exec_status.get('currentStatus') == 'UNAVAILABLE_CLEARANCES':
            return jsonify({
                'mode': 'integraicp',
                'error': 'Nenhum provedor ICP-Brasil disponível',
                'message': 'O CPF informado não possui certificado digital em nuvem cadastrado nos provedores disponíveis (VIDaaS, BirdID, etc). Cadastre-se em um provedor primeiro.'
            }), 404

        # Salvar sessão de assinatura pendente
        sig_session = {
            'id': f'SIG{uuid.uuid4().hex[:8].upper()}',
            'session_id': session_id,
            'doc_type': doc_type,
            'doc_id': doc_id,
            'medico_nome': medico_nome,
            'medico_crm': medico_crm,
            'medico_cpf': medico_cpf,
            'doc_hash': doc_hash,
            'code_verifier': pkce['code_verifier'],
            'code_challenge': pkce['code_challenge'],
            'status': 'pending_authentication',
            'credential_id': None,
            'signature_data': None,
            'request_id': data_obj.get('requestId', ''),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        sigs = load_assinaturas()
        sigs.append(sig_session)
        save_assinaturas(sigs)

        logger.info(f"IntegraICP: {len(clearances)} provedor(es) encontrado(s) para session={session_id}")

        # Retorna clearances para o frontend selecionar provedor (Passo 2 do diagrama)
        return jsonify({
            'mode': 'integraicp',
            'session_id': session_id,
            'clearances': clearances,
            'expire_timestamp': data_obj.get('expireTimestamp', ''),
            'message': 'Selecione o provedor de certificado digital para autenticação'
        })

    # ── Modo Simulado (fallback) ──
    signature_record = {
        'id': f'SIG{uuid.uuid4().hex[:8].upper()}',
        'doc_type': doc_type,
        'doc_id': doc_id,
        'provider': provider,
        'medico_nome': medico_nome,
        'medico_crm': medico_crm,
        'doc_hash': doc_hash,
        'status': 'signed',
        'signed_at': datetime.now(timezone.utc).isoformat(),
        'signature_certificate': f"CERT-{doc_hash[:16]}-ICP-BR",
        'created_at': datetime.now(timezone.utc).isoformat()
    }

    _update_document_signature(doc_type, doc_id, doc_hash, provider, signature_record['signed_at'])

    sigs = load_assinaturas()
    sigs.append(signature_record)
    save_assinaturas(sigs)

    return jsonify({
        'mode': 'simulated',
        'signature': signature_record,
        'message': f'Documento assinado digitalmente via {provider.upper()} (modo simulado)'
    })


@app.route('/api/assinatura/callback', methods=['GET', 'POST'])
def callback_assinatura():
    """
    Callback do IntegraICP após autenticação do médico no provedor.
    Conforme diagrama: GET myapp.com/callback?code={CredentialId}
    O param 'code' contém o CredentialId retornado pelo IntegraICP.
    """
    # IntegraICP envia CredentialId como ?code={CredentialId} conforme diagrama
    credential_id = (
        request.args.get('code') or
        request.args.get('credentialId') or
        request.args.get('credential_id', '')
    )
    session_id = request.args.get('session_id', '')
    doc_type = request.args.get('doc_type', '')
    doc_id = request.args.get('doc_id', '')

    # Também aceita via JSON body (fallback)
    if not credential_id and request.is_json:
        body = request.get_json(silent=True) or {}
        credential_id = body.get('code', body.get('credentialId', body.get('credential_id', '')))
        session_id = session_id or body.get('session_id', '')

    logger.info(f"Assinatura callback: credential_id={credential_id}, session_id={session_id}")

    if credential_id and session_id:
        sigs = load_assinaturas()
        for sig in sigs:
            if sig.get('session_id') == session_id:
                sig['credential_id'] = credential_id
                sig['status'] = 'authenticated'
                sig['authenticated_at'] = datetime.now(timezone.utc).isoformat()
                break
        save_assinaturas(sigs)

    # Redirecionar de volta para a plataforma com status
    return redirect(f'/?signature_callback=true&session_id={session_id}&status=authenticated')


@app.route('/api/assinatura/executar', methods=['POST'])
def executar_assinatura():
    """
    Executa a assinatura digital completa SERVER-SIDE após callback com CredentialId.
    Conforme diagrama de sequência IntegraICP:
    1. GET /credentials/{credentialId}?secret_data={code_verifier} → dados do certificado
    2. POST /signatures com credentialId + code_verifier + SHA256 Base64 → assinatura digital
    
    Tudo feito server-side (sem expor code_verifier ao browser).
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id', '')

    sigs = load_assinaturas()
    sig = next((s for s in sigs if s.get('session_id') == session_id), None)
    if not sig:
        return jsonify({'error': 'Sessão de assinatura não encontrada'}), 404
    if sig.get('status') not in ('authenticated', 'signing'):
        return jsonify({'error': f'Status inválido: {sig.get("status")}. Médico precisa autenticar primeiro.'}), 400

    credential_id = sig.get('credential_id')
    code_verifier = sig.get('code_verifier')

    if not credential_id or not code_verifier:
        return jsonify({'error': 'Credenciais incompletas'}), 400

    if not integraicp or not integraicp.is_configured():
        return jsonify({'error': 'IntegraICP não configurado'}), 500

    sig['status'] = 'signing'
    save_assinaturas(sigs)

    try:
        # ── Passo 1: GET /credentials — obter dados do certificado ──
        cred_result = integraicp.get_credential(credential_id, code_verifier)
        if 'error' in cred_result:
            sig['status'] = 'error'
            sig['error_detail'] = str(cred_result.get('error', ''))
            save_assinaturas(sigs)
            return jsonify({
                'error': 'Erro ao obter credenciais do certificado',
                'detail': cred_result
            }), 400

        cert_info = cred_result.get('data', {}).get('certificateInformation', {})
        subject_info = cred_result.get('data', {}).get('subjectIdentification', {})

        # Salvar dados do certificado na sessão
        sig['certificate_subject'] = cert_info.get('subjectName', '')
        sig['certificate_issuer'] = cert_info.get('issuerName', '')
        sig['certificate_serial'] = cert_info.get('serialNumber', '')
        sig['certificate_fingerprint'] = cert_info.get('fingerprint256', '')
        sig['certificate_validity'] = cert_info.get('validity', {})
        sig['signer_cpf'] = subject_info.get('identificationKey', '')
        save_assinaturas(sigs)

        # ── Passo 2: POST /signatures — assinar documento ──
        sig_result = integraicp.sign_documents(
            credential_id=credential_id,
            code_verifier=code_verifier,
            documents=[{
                'content_id': sig.get('doc_id', ''),
                'content_hash_hex': sig.get('doc_hash', ''),
                'description': f"{sig.get('doc_type', 'documento')} - {sig.get('medico_nome', '')}"
            }],
            signature_policy='CMS'
        )

        if 'error' in sig_result:
            sig['status'] = 'error'
            sig['error_detail'] = str(sig_result.get('error', ''))
            save_assinaturas(sigs)
            return jsonify({
                'error': 'Erro ao executar assinatura digital',
                'detail': sig_result
            }), 400

        # ── Sucesso: extrair dados da assinatura ──
        exec_status = sig_result.get('data', {}).get('executionStatus', {})
        signatures = sig_result.get('data', {}).get('signatures', [])

        signed_content = signatures[0].get('signedContent', '') if signatures else ''
        signature_timestamp = signatures[0].get('signatureTimestamp', '') if signatures else ''
        signature_id = signatures[0].get('signatureId', '') if signatures else ''

        sig['status'] = 'signed'
        sig['signed_at'] = signature_timestamp or datetime.now(timezone.utc).isoformat()
        sig['signed_content'] = signed_content
        sig['signature_id_icp'] = signature_id
        sig['integraicp_status'] = exec_status.get('currentStatus', '')
        sig['signature_data'] = sig_result
        save_assinaturas(sigs)

        # Atualizar documento original (prescrição/laudo)
        _update_document_signature(
            sig.get('doc_type'), sig.get('doc_id'),
            sig.get('doc_hash'), 'integraicp', sig['signed_at']
        )

        # Também atualizar certificado do médico (se tiver doctor_id)
        if sig.get('medico_cpf'):
            docs = load_doctors()
            for d in docs:
                cpf_cert = (d.get('certificado_digital', {}).get('cpf', '') or d.get('cpf', ''))
                if cpf_cert == sig['medico_cpf']:
                    d['certificado_digital'] = d.get('certificado_digital', {})
                    d['certificado_digital'].update({
                        'certificado_nome': cert_info.get('subjectName', ''),
                        'certificado_emissor': cert_info.get('issuerName', ''),
                        'certificado_serial': cert_info.get('serialNumber', ''),
                        'certificado_validade': cert_info.get('validity', {}).get('notAfter', ''),
                        'status': 'vinculado',
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    })
                    break
            save_doctors(docs)

        logger.info(f"✅ Assinatura digital concluída: session={session_id}, doc={sig.get('doc_id')}")

        return jsonify({
            'status': 'signed',
            'session_id': session_id,
            'certificate_subject': sig.get('certificate_subject', ''),
            'certificate_issuer': sig.get('certificate_issuer', ''),
            'signer_cpf': sig.get('signer_cpf', ''),
            'signed_at': sig.get('signed_at', ''),
            'message': 'Documento assinado digitalmente via ICP-Brasil (IntegraICP)'
        })

    except Exception as e:
        logger.error(f"Erro na assinatura digital: {e}")
        sig['status'] = 'error'
        sig['error_detail'] = str(e)
        save_assinaturas(sigs)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500


@app.route('/api/assinatura/confirmar', methods=['POST'])
def confirmar_assinatura():
    """
    Endpoint legado — a confirmação agora é feita automaticamente em /executar.
    Mantido para compatibilidade.
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id', '')
    sigs = load_assinaturas()
    sig = next((s for s in sigs if s.get('session_id') == session_id), None)
    if not sig:
        return jsonify({'error': 'Sessão não encontrada'}), 404
    # Retornar status atual
    safe = {k: v for k, v in sig.items() if k not in ('code_verifier', 'code_challenge')}
    return jsonify({'signature': safe, 'message': f'Status: {sig.get("status")}'})


@app.route('/api/assinatura/status/<session_id>', methods=['GET'])
def status_assinatura(session_id):
    """Consulta o status de uma sessão de assinatura."""
    sigs = load_assinaturas()
    sig = next((s for s in sigs if s.get('session_id') == session_id), None)
    if not sig:
        return jsonify({'error': 'Sessão não encontrada'}), 404
    # Não expor code_verifier na resposta
    safe = {k: v for k, v in sig.items() if k not in ('code_verifier', 'code_challenge')}
    return jsonify(safe)


def _update_document_signature(doc_type, doc_id, doc_hash, provider, signed_at):
    """Atualiza o documento original com dados da assinatura."""
    if doc_type == 'prescricao':
        prescricoes = load_prescricoes()
        for p in prescricoes:
            if p.get('id') == doc_id:
                p['is_signed'] = True
                p['signature_hash'] = doc_hash
                p['signature_provider'] = provider
                p['signed_at'] = signed_at
                break
        save_prescricoes(prescricoes)
    elif doc_type == 'laudo':
        laudos_data = load_laudos()
        for l in laudos_data:
            if l.get('id') == doc_id:
                l['is_signed'] = True
                l['signature_hash'] = doc_hash
                l['status'] = 'assinado'
                l['signed_at'] = signed_at
                break
        save_laudos(laudos_data)


# ===== CERTIFICADO DIGITAL DO MÉDICO =====
@app.route('/api/doctors/<doc_id>/certificado', methods=['GET'])
def get_certificado_medico(doc_id):
    """Retorna dados do certificado digital do médico."""
    docs = load_doctors()
    doc = next((d for d in docs if d.get('id') == doc_id), None)
    if not doc:
        return jsonify({'error': 'Médico não encontrado'}), 404
    cert = doc.get('certificado_digital', {})
    return jsonify(cert)


@app.route('/api/doctors/<doc_id>/certificado', methods=['PUT'])
def update_certificado_medico(doc_id):
    """Atualiza dados do certificado digital do médico."""
    docs = load_doctors()
    idx = next((i for i, d in enumerate(docs) if d.get('id') == doc_id), None)
    if idx is None:
        return jsonify({'error': 'Médico não encontrado'}), 404

    data = request.get_json(silent=True) or {}
    cert = docs[idx].get('certificado_digital', {})
    cert.update({
        'cpf': data.get('cpf', cert.get('cpf', '')),
        'provedor_preferido': data.get('provedor_preferido', cert.get('provedor_preferido', 'integraicp')),
        'credential_id': data.get('credential_id', cert.get('credential_id', '')),
        'certificado_nome': data.get('certificado_nome', cert.get('certificado_nome', '')),
        'certificado_emissor': data.get('certificado_emissor', cert.get('certificado_emissor', '')),
        'certificado_validade': data.get('certificado_validade', cert.get('certificado_validade', '')),
        'certificado_serial': data.get('certificado_serial', cert.get('certificado_serial', '')),
        'status': data.get('status', cert.get('status', 'pendente')),
        'updated_at': datetime.now(timezone.utc).isoformat()
    })
    docs[idx]['certificado_digital'] = cert
    save_doctors(docs)
    return jsonify(cert)


@app.route('/api/doctors/<doc_id>/certificado/vincular', methods=['POST'])
def vincular_certificado_medico(doc_id):
    """
    Inicia o processo de vinculação do certificado digital do médico.
    Retorna a URL de autenticação IntegraICP para o médico se autenticar.
    """
    docs = load_doctors()
    doc = next((d for d in docs if d.get('id') == doc_id), None)
    if not doc:
        return jsonify({'error': 'Médico não encontrado'}), 404

    data = request.get_json(silent=True) or {}
    cpf = data.get('cpf', '')
    if not cpf:
        return jsonify({'error': 'CPF é obrigatório para vincular certificado'}), 400

    if not integraicp or not integraicp.is_configured():
        # Modo simulado
        cert = doc.get('certificado_digital', {})
        cert.update({
            'cpf': cpf,
            'status': 'vinculado_simulado',
            'provedor_preferido': 'simulado',
            'certificado_nome': doc.get('nome', doc.get('name', '')),
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        docs_list = load_doctors()
        for d in docs_list:
            if d.get('id') == doc_id:
                d['certificado_digital'] = cert
                break
        save_doctors(docs_list)
        return jsonify({'mode': 'simulated', 'certificado': cert, 'message': 'Certificado vinculado (modo simulado)'})

    pkce = integraicp.generate_pkce_pair()
    session_id = f'CERT_{uuid.uuid4().hex[:12]}'
    callback_uri = f"{integraicp.callback_base_url}/api/doctors/{doc_id}/certificado/callback?session_id={session_id}"

    auth_url = integraicp.get_authentications_url(
        code_challenge=pkce['code_challenge'],
        callback_uri=callback_uri,
        subject_key=cpf,
        credential_lifetime=600
    )

    # Salvar sessão temporária
    sigs = load_assinaturas()
    sigs.append({
        'id': session_id,
        'session_id': session_id,
        'type': 'certificate_binding',
        'doctor_id': doc_id,
        'cpf': cpf,
        'code_verifier': pkce['code_verifier'],
        'status': 'pending_authentication',
        'created_at': datetime.now(timezone.utc).isoformat()
    })
    save_assinaturas(sigs)

    return jsonify({
        'mode': 'integraicp',
        'session_id': session_id,
        'auth_url': auth_url,
        'message': 'Redirecionar o médico para autenticação'
    })


@app.route('/api/doctors/<doc_id>/certificado/callback', methods=['GET'])
def callback_certificado_medico(doc_id):
    """Callback após autenticação do médico para vinculação de certificado."""
    # IntegraICP envia ?code={CredentialId} conforme diagrama
    credential_id = (
        request.args.get('code') or
        request.args.get('credentialId') or
        request.args.get('credential_id', '')
    )
    session_id = request.args.get('session_id', '')

    if credential_id and session_id:
        sigs = load_assinaturas()
        sig = next((s for s in sigs if s.get('session_id') == session_id), None)
        if sig:
            sig['credential_id'] = credential_id
            sig['status'] = 'authenticated'
            save_assinaturas(sigs)

            # Atualizar certificado do médico
            docs = load_doctors()
            for d in docs:
                if d.get('id') == doc_id:
                    d['certificado_digital'] = d.get('certificado_digital', {})
                    d['certificado_digital'].update({
                        'cpf': sig.get('cpf', ''),
                        'credential_id': credential_id,
                        'status': 'vinculado',
                        'provedor_preferido': 'integraicp',
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    })
                    break
            save_doctors(docs)

    return redirect(f'/?cert_callback=true&doctor_id={doc_id}&status=vinculado')


# ===== SOLICITAÇÕES DE EXAMES API =====
@app.route('/api/pacientes/<pac_id>/solicitacao', methods=['POST'])
def criar_solicitacao(pac_id):
    """Create a signed exam/test solicitation and save to prontuário annexos"""
    pacientes = load_pacientes()
    pac = next((p for p in pacientes if p.get('id') == pac_id), None)
    if not pac:
        return jsonify({'error': 'Paciente não encontrado'}), 404

    data = request.get_json(silent=True) or {}
    tipo_solicitacao = data.get('tipo_solicitacao', '')  # 'exames_laboratoriais' or 'teste_farmacogenetico'
    exames = data.get('exames', [])
    observacoes = data.get('observacoes', '')
    medico_nome = data.get('medico_nome', '')
    medico_crm = data.get('medico_crm', '')

    if not exames:
        return jsonify({'error': 'Nenhum exame selecionado'}), 400

    # Build structured content for document renderer
    if tipo_solicitacao == 'exames_laboratoriais':
        titulo = f"Solicitação de Exames Laboratoriais - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        tipo_label = 'Exames Laboratoriais'
    else:
        titulo = f"Solicitação de Teste Farmacogenético - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        tipo_label = 'Teste Farmacogenético'

    conteudo_lines = [f"TIPO_SOLICITACAO: {tipo_solicitacao}"]
    conteudo_lines.append(f"TITULO: {tipo_label}")
    for exame in exames:
        conteudo_lines.append(f"EXAME: {exame}")
    if observacoes:
        conteudo_lines.append(f"OBSERVAÇÕES: {observacoes}")
    conteudo_lines.append(f"{medico_nome}")
    conteudo_lines.append(f"{medico_crm}")

    conteudo = '\n'.join(conteudo_lines)

    # Save to prontuário as anexo
    prontuarios = load_prontuarios()
    pron_record = {
        'id': f'PRON{len(prontuarios)+1:05d}',
        'paciente_id': pac_id,
        'tipo': 'anexo',
        'titulo': titulo,
        'descricao': ', '.join(exames),
        'conteudo': conteudo,
        'arquivo_url': '',
        'medico_id': '',
        'medico_nome': medico_nome,
        'data': datetime.now(timezone.utc).isoformat(),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    prontuarios.append(pron_record)
    save_prontuarios(prontuarios)

    # Add timeline event
    add_timeline_event(pac_id, 'solicitacao', f'Solicitação: {tipo_label}',
        f'{medico_nome} solicitou: {", ".join(exames)}')

    return jsonify({
        'prontuario': pron_record,
        'message': f'Solicitação assinada e salva nos anexos do paciente'
    }), 201


# ===== ASSINATURA CONFIG API =====
ASSINATURA_CONFIG_FILE = os.path.join(DATA_DIR, 'assinatura_config.json')

def load_assinatura_config():
    return _load_json_file(ASSINATURA_CONFIG_FILE, {
        'integraicp_channel_id': '',
        'integraicp_callback_url': 'https://app.onmedicinainternacional.com',
        'intellisign_client_id': '',
        'intellisign_client_secret': '',
        'intellisign_organization': ''
    })

def save_assinatura_config(data):
    _save_json_file(ASSINATURA_CONFIG_FILE, data)


@app.route('/api/assinatura-config', methods=['GET'])
def get_assinatura_config():
    """Retorna configuração de assinatura digital (mascarando secrets)"""
    config = load_assinatura_config()
    # Ler também do .env como fallback
    env_icp_channel = os.environ.get('INTEGRAICP_CHANNEL_ID', '')
    env_icp_callback = os.environ.get('INTEGRAICP_CALLBACK_URL', 'https://app.onmedicinainternacional.com')
    env_is_client_id = os.environ.get('INTELLISIGN_CLIENT_ID', '')
    env_is_client_secret = os.environ.get('INTELLISIGN_CLIENT_SECRET', '')

    channel_id = config.get('integraicp_channel_id') or env_icp_channel
    callback_url = config.get('integraicp_callback_url') or env_icp_callback
    client_id = config.get('intellisign_client_id') or env_is_client_id
    client_secret = config.get('intellisign_client_secret') or env_is_client_secret
    organization = config.get('intellisign_organization', '')

    # Mascarar secret
    masked_secret = ''
    if client_secret:
        if len(client_secret) > 8:
            masked_secret = client_secret[:4] + '••••••••' + client_secret[-4:]
        else:
            masked_secret = '••••••••'

    return jsonify({
        'integraicp_channel_id': channel_id,
        'integraicp_callback_url': callback_url,
        'integraicp_configured': bool(channel_id),
        'intellisign_client_id': client_id,
        'intellisign_client_secret_masked': masked_secret,
        'intellisign_organization': organization,
        'intellisign_configured': bool(client_id and client_secret)
    })


@app.route('/api/assinatura-config', methods=['POST'])
def update_assinatura_config():
    """Atualiza configuração de assinatura digital e recarrega serviços"""
    data = request.get_json(silent=True) or {}
    config = load_assinatura_config()

    updated_env = False

    # IntegraICP
    if 'integraicp_channel_id' in data:
        config['integraicp_channel_id'] = data['integraicp_channel_id']
        os.environ['INTEGRAICP_CHANNEL_ID'] = data['integraicp_channel_id']
        updated_env = True
    if 'integraicp_callback_url' in data:
        config['integraicp_callback_url'] = data['integraicp_callback_url']
        os.environ['INTEGRAICP_CALLBACK_URL'] = data['integraicp_callback_url']

    # Intellisign
    if 'intellisign_client_id' in data:
        config['intellisign_client_id'] = data['intellisign_client_id']
        os.environ['INTELLISIGN_CLIENT_ID'] = data['intellisign_client_id']
        updated_env = True
    if 'intellisign_client_secret' in data:
        config['intellisign_client_secret'] = data['intellisign_client_secret']
        os.environ['INTELLISIGN_CLIENT_SECRET'] = data['intellisign_client_secret']
        updated_env = True
    if 'intellisign_organization' in data:
        config['intellisign_organization'] = data['intellisign_organization']

    save_assinatura_config(config)

    # Atualizar .env file
    try:
        env_path = os.path.join(BASE_DIR, '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.read()

            env_updates = {
                'INTEGRAICP_CHANNEL_ID': config.get('integraicp_channel_id', ''),
                'INTEGRAICP_CALLBACK_URL': config.get('integraicp_callback_url', ''),
                'INTELLISIGN_CLIENT_ID': config.get('intellisign_client_id', ''),
                'INTELLISIGN_CLIENT_SECRET': config.get('intellisign_client_secret', ''),
            }

            for key, value in env_updates.items():
                if value:
                    import re
                    pattern = re.compile(rf'^{key}=.*$', re.MULTILINE)
                    if pattern.search(env_content):
                        env_content = pattern.sub(f'{key}={value}', env_content)
                    else:
                        env_content += f'\n{key}={value}'

            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
    except Exception as e:
        logger.warning(f"Erro ao atualizar .env: {e}")

    # Recarregar serviços IntegraICP
    global integraicp
    try:
        from integraicp_service import IntegraICPService
        integraicp = IntegraICPService()
        if integraicp.is_configured():
            logger.info("✅ IntegraICP reconfigurado com sucesso")
        else:
            logger.warning("⚠️ IntegraICP ainda sem channel_id")
    except Exception as e:
        logger.warning(f"Erro ao recarregar IntegraICP: {e}")

    # Recarregar Intellisign
    global intellisign
    try:
        from intellisign_service import IntellisignService
        intellisign = IntellisignService()
        logger.info("✅ Intellisign reconfigurado com sucesso")
    except Exception as e:
        logger.warning(f"Erro ao recarregar Intellisign: {e}")

    return jsonify({'success': True, 'message': 'Configurações salvas com sucesso'})


@app.route('/api/assinatura-config/test/<provider>', methods=['POST'])
def test_assinatura_connection(provider):
    """Testa conexão com provedor de assinatura"""
    if provider == 'integraicp':
        channel_id = os.environ.get('INTEGRAICP_CHANNEL_ID', '')
        if not channel_id:
            return jsonify({'success': False, 'error': 'Channel ID não configurado'}), 400
        try:
            # Testar conectividade com IntegraICP
            import requests as req
            resp = req.get(
                f'https://services.integraicp.com.br/{channel_id}/authentications',
                params={'code_challenge': 'test', 'code_challenge_method': 'S256'},
                timeout=10
            )
            if resp.status_code in [200, 400, 401]:
                return jsonify({'success': True, 'message': f'Conexão OK (HTTP {resp.status_code})'})
            return jsonify({'success': False, 'error': f'Resposta inesperada: HTTP {resp.status_code}'})
        except Exception as e:
            return jsonify({'success': False, 'error': f'Erro de conexão: {str(e)}'}), 500

    elif provider == 'intellisign':
        client_id = os.environ.get('INTELLISIGN_CLIENT_ID', '')
        client_secret = os.environ.get('INTELLISIGN_CLIENT_SECRET', '')
        if not client_id or not client_secret:
            return jsonify({'success': False, 'error': 'Client ID ou Client Secret não configurados'}), 400
        try:
            import requests as req
            resp = req.post(
                'https://api.intellisign.com/oauth/token',
                data={
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret
                },
                timeout=10
            )
            if resp.status_code == 200:
                token_data = resp.json()
                return jsonify({
                    'success': True,
                    'message': f'Autenticação OK! Token válido por {token_data.get("expires_in", "?")}s'
                })
            else:
                err_msg = resp.json().get('error_description', resp.text[:200]) if resp.text else f'HTTP {resp.status_code}'
                return jsonify({'success': False, 'error': f'Falha na autenticação: {err_msg}'})
        except Exception as e:
            return jsonify({'success': False, 'error': f'Erro de conexão: {str(e)}'}), 500

    return jsonify({'success': False, 'error': 'Provedor desconhecido'}), 400


# ===== WEBHOOKS CONFIG API =====
@app.route('/api/webhooks-config', methods=['GET'])
def get_webhooks_config():
    """Get webhook configuration"""
    config = load_webhooks_config()
    return jsonify(config)


@app.route('/api/webhooks-config', methods=['POST'])
def update_webhooks_config():
    """Update webhook configuration"""
    data = request.get_json(silent=True) or {}
    config = load_webhooks_config()
    if 'prescricao_url' in data:
        config['prescricao_url'] = data['prescricao_url']
    if 'prescricao_ativo' in data:
        config['prescricao_ativo'] = bool(data['prescricao_ativo'])
    save_webhooks_config(config)
    return jsonify(config)


@app.route('/api/webhooks-config/test', methods=['POST'])
def test_webhook():
    """Test webhook by sending a test payload"""
    config = load_webhooks_config()
    url = config.get('prescricao_url', '')
    if not url:
        return jsonify({'error': 'URL de webhook não configurada'}), 400
    try:
        import requests as req
        test_payload = {
            'evento': 'teste_webhook',
            'mensagem': 'Teste de webhook da Plataforma ON Medicina Internacional',
            'data': datetime.now(timezone.utc).isoformat()
        }
        resp = req.post(url, json=test_payload, headers={'Content-Type': 'application/json'}, timeout=10)
        return jsonify({'success': True, 'status_code': resp.status_code, 'message': f'Webhook enviado com status {resp.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== INTELLISIGN — Assinatura Eletrônica de Documentos (Pacientes) =====
ENVELOPES_FILE = os.path.join(DATA_DIR, 'intellisign_envelopes.json')

def load_envelopes():
    return _load_json_file(ENVELOPES_FILE, [])

def save_envelopes(data):
    _save_json_file(ENVELOPES_FILE, data)

try:
    from intellisign_service import IntellisignService
    intellisign = IntellisignService()
    if intellisign.is_configured():
        logger.info("✅ Intellisign configurado — assinatura de pacientes ativa")
    else:
        logger.warning("⚠️ Intellisign sem credenciais — modo desabilitado")
        intellisign = None
except ImportError:
    intellisign = None
    logger.warning("⚠️ intellisign_service.py não encontrado — assinatura de pacientes indisponível")


def _gerar_pdf_prescricao(prescricao, paciente) -> bytes:
    """Gera PDF simples de prescrição usando reportlab ou fallback texto."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas as pdf_canvas
        from io import BytesIO

        buf = BytesIO()
        c = pdf_canvas.Canvas(buf, pagesize=A4)
        w, h = A4

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(w/2, h - 40*mm, "ON Medicina Internacional")
        c.setFont("Helvetica", 10)
        c.drawCentredString(w/2, h - 47*mm, "Receituário Médico")

        # Line separator
        c.setStrokeColorRGB(0.1, 0.1, 0.1)
        c.line(20*mm, h - 52*mm, w - 20*mm, h - 52*mm)

        # Patient info
        y = h - 62*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20*mm, y, f"Paciente: {paciente.get('nome', 'N/A').upper()}")
        c.setFont("Helvetica", 9)
        y -= 6*mm
        c.drawString(20*mm, y, f"CPF: {paciente.get('cpf', 'N/A')}     Data de Nascimento: {paciente.get('data_nascimento', 'N/A')}")
        y -= 6*mm
        c.drawString(20*mm, y, f"Data: {prescricao.get('data', '')[:10]}     Médico: {prescricao.get('medico_nome', '')} — {prescricao.get('medico_crm', '')}")

        # Medications
        y -= 12*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20*mm, y, "Prescrição:")
        y -= 8*mm

        medicamentos = prescricao.get('medicamentos', [])
        for i, med in enumerate(medicamentos, 1):
            c.setFont("Helvetica-Bold", 10)
            nome = med.get('nome', f'Medicamento {i}')
            c.drawString(22*mm, y, f"{i}. {nome}")
            y -= 5*mm

            c.setFont("Helvetica", 9)
            detalhes = []
            if med.get('concentracao'):
                detalhes.append(f"Concentração: {med['concentracao']}")
            if med.get('volume'):
                detalhes.append(f"Volume: {med['volume']}")
            if med.get('laboratorio'):
                detalhes.append(f"Laboratório: {med['laboratorio']}")
            if med.get('tipo'):
                detalhes.append(f"Tipo: {med['tipo']}")
            if detalhes:
                c.drawString(28*mm, y, " | ".join(detalhes))
                y -= 5*mm

            posologia = med.get('posologia', '')
            if posologia:
                c.drawString(28*mm, y, f"Posologia: {posologia}")
                y -= 5*mm

            y -= 3*mm
            if y < 40*mm:
                c.showPage()
                y = h - 30*mm

        # Observations
        obs = prescricao.get('observacoes', '')
        if obs:
            y -= 5*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(20*mm, y, "Observações:")
            y -= 5*mm
            c.setFont("Helvetica", 9)
            for line in obs.split('\n')[:10]:
                c.drawString(22*mm, y, line[:90])
                y -= 4.5*mm

        # Signature area
        y -= 15*mm
        if y < 60*mm:
            c.showPage()
            y = h - 80*mm

        c.line(w/2 - 40*mm, y, w/2 + 40*mm, y)
        y -= 5*mm
        c.setFont("Helvetica", 9)
        c.drawCentredString(w/2, y, f"{prescricao.get('medico_nome', '')}")
        y -= 4*mm
        c.drawCentredString(w/2, y, f"{prescricao.get('medico_crm', '')}")

        # Footer
        c.setFont("Helvetica", 7)
        c.drawCentredString(w/2, 15*mm, "ON Medicina Internacional — Documento gerado eletronicamente")
        c.drawCentredString(w/2, 11*mm, f"Válido por {prescricao.get('duracao_meses', 24)} meses a partir de {prescricao.get('data', '')[:10]}")

        c.save()
        return buf.getvalue()

    except ImportError:
        # Fallback: gerar texto simples como PDF-like content
        content = f"RECEITUÁRIO MÉDICO — ON Medicina Internacional\n\n"
        content += f"Paciente: {paciente.get('nome', 'N/A')}\n"
        content += f"CPF: {paciente.get('cpf', 'N/A')}\n"
        content += f"Data: {prescricao.get('data', '')}\n"
        content += f"Médico: {prescricao.get('medico_nome', '')} — {prescricao.get('medico_crm', '')}\n\n"
        for med in prescricao.get('medicamentos', []):
            content += f"- {med.get('nome', '')}: {med.get('posologia', '')}\n"
        return content.encode('utf-8')


def _gerar_pdf_laudo(laudo, paciente) -> bytes:
    """Gera PDF de laudo médico circunstanciado."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas as pdf_canvas
        from io import BytesIO

        buf = BytesIO()
        c = pdf_canvas.Canvas(buf, pagesize=A4)
        w, h = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(w/2, h - 40*mm, "ON Medicina Internacional")
        c.setFont("Helvetica", 11)
        c.drawCentredString(w/2, h - 48*mm, "Laudo Médico Circunstanciado")

        c.line(20*mm, h - 53*mm, w - 20*mm, h - 53*mm)

        y = h - 63*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20*mm, y, f"Paciente: {paciente.get('nome', 'N/A').upper()}")
        y -= 6*mm
        c.setFont("Helvetica", 9)
        c.drawString(20*mm, y, f"CPF: {paciente.get('cpf', 'N/A')}")

        campos = [
            ('Diagnóstico (CID)', laudo.get('diagnostico_cid', '')),
            ('Histórico Clínico', laudo.get('historico_clinico', '')),
            ('Tratamentos Anteriores', laudo.get('tratamentos_anteriores', '')),
            ('Medicações Atuais', laudo.get('medicacoes_atuais', '')),
            ('Justificativa Cannabis', laudo.get('justificativa_cannabis', '')),
            ('Conclusão', laudo.get('conclusao', ''))
        ]

        for label, val in campos:
            if not val:
                continue
            y -= 10*mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(20*mm, y, f"{label}:")
            y -= 5*mm
            c.setFont("Helvetica", 9)
            # Wrap text
            words = val.split()
            line = ''
            for word in words:
                test = line + ' ' + word if line else word
                if len(test) > 85:
                    c.drawString(22*mm, y, line)
                    y -= 4.5*mm
                    line = word
                    if y < 35*mm:
                        c.showPage()
                        y = h - 30*mm
                else:
                    line = test
            if line:
                c.drawString(22*mm, y, line)
                y -= 4.5*mm

        # Signature
        y -= 15*mm
        if y < 50*mm:
            c.showPage()
            y = h - 80*mm
        c.line(w/2 - 40*mm, y, w/2 + 40*mm, y)
        y -= 5*mm
        c.setFont("Helvetica", 9)
        c.drawCentredString(w/2, y, laudo.get('medico_nome', ''))
        y -= 4*mm
        c.drawCentredString(w/2, y, laudo.get('medico_crm', ''))

        c.setFont("Helvetica", 7)
        c.drawCentredString(w/2, 15*mm, "ON Medicina Internacional — Documento gerado eletronicamente")

        c.save()
        return buf.getvalue()

    except ImportError:
        content = f"LAUDO MÉDICO CIRCUNSTANCIADO\n\nPaciente: {paciente.get('nome', '')}\n"
        for k in ('diagnostico_cid', 'historico_clinico', 'justificativa_cannabis', 'conclusao'):
            content += f"\n{k}: {laudo.get(k, '')}\n"
        return content.encode('utf-8')


@app.route('/api/intellisign/enviar', methods=['POST'])
def intellisign_enviar():
    """
    Envia documento para assinatura do paciente via Intellisign.
    Gera PDF, faz upload, cria envelope, adiciona destinatário e envia.
    """
    if not intellisign:
        return jsonify({'error': 'Intellisign não configurado. Adicione INTELLISIGN_CLIENT_ID e INTELLISIGN_CLIENT_SECRET no .env'}), 503

    data = request.get_json(silent=True) or {}
    paciente_id = data.get('paciente_id', '')
    doc_type = data.get('doc_type', '')  # 'prescricao' ou 'laudo'
    doc_id = data.get('doc_id', '')
    canal = data.get('canal', 'email')  # 'email' ou 'whatsapp'
    mensagem_extra = data.get('mensagem', '')
    signature_type = data.get('signature_type', 'simple')

    # Buscar paciente
    pacientes = load_pacientes()
    pac = next((p for p in pacientes if p.get('id') == paciente_id), None)
    if not pac:
        return jsonify({'error': 'Paciente não encontrado'}), 404

    pac_email = pac.get('email', '')
    pac_telefone = pac.get('telefone', '')
    pac_nome = pac.get('nome', '')

    if canal == 'email' and not pac_email:
        return jsonify({'error': 'Paciente não possui email cadastrado'}), 400
    if canal == 'whatsapp' and not pac_telefone:
        return jsonify({'error': 'Paciente não possui telefone cadastrado'}), 400

    # Buscar documento e gerar PDF
    pdf_bytes = None
    filename = ''
    doc_titulo = ''

    if doc_type == 'prescricao':
        prescricoes = load_prescricoes()
        presc = next((p for p in prescricoes if p.get('id') == doc_id), None)
        if not presc:
            return jsonify({'error': 'Prescrição não encontrada'}), 404
        pdf_bytes = _gerar_pdf_prescricao(presc, pac)
        filename = f"Prescricao_{pac_nome.replace(' ', '_')}_{doc_id}.pdf"
        doc_titulo = f"Prescrição Cannabis — {pac_nome}"

    elif doc_type == 'laudo':
        laudos = load_laudos()
        laudo = next((l for l in laudos if l.get('id') == doc_id), None)
        if not laudo:
            return jsonify({'error': 'Laudo não encontrado'}), 404
        pdf_bytes = _gerar_pdf_laudo(laudo, pac)
        filename = f"Laudo_{pac_nome.replace(' ', '_')}_{doc_id}.pdf"
        doc_titulo = f"Laudo Médico — {pac_nome}"

    else:
        return jsonify({'error': 'Tipo de documento inválido. Use: prescricao ou laudo'}), 400

    if not pdf_bytes:
        return jsonify({'error': 'Erro ao gerar PDF'}), 500

    # Enviar via Intellisign
    try:
        assunto = f"ON Medicina — {doc_titulo} — Assinatura necessária"
        msg = mensagem_extra or (
            f"Olá {pac_nome},\n\n"
            f"Segue o documento '{doc_titulo}' para sua assinatura.\n"
            f"Por favor, clique no link abaixo para assinar eletronicamente.\n\n"
            f"Atenciosamente,\nON Medicina Internacional"
        )

        result = intellisign.enviar_para_assinatura(
            pdf_bytes=pdf_bytes,
            filename=filename,
            paciente_nome=pac_nome,
            paciente_email=pac_email if canal == 'email' else None,
            paciente_telefone=pac_telefone if canal == 'whatsapp' else None,
            assunto=assunto,
            mensagem=msg,
            titulo=doc_titulo,
            expire_days=30,
            signature_type=signature_type
        )

        if result.get('error'):
            return jsonify(result), result.get('status_code', 500)

        # Salvar registro do envelope
        envelope_record = {
            'id': result.get('envelope_id', ''),
            'hashid': result.get('hashid', ''),
            'paciente_id': paciente_id,
            'paciente_nome': pac_nome,
            'doc_type': doc_type,
            'doc_id': doc_id,
            'doc_titulo': doc_titulo,
            'canal': canal,
            'enviado_para': result.get('enviado_para', ''),
            'status': 'in-transit',
            'signature_type': signature_type,
            'file_item_id': result.get('file_item_id', ''),
            'document_id': result.get('document_id', ''),
            'recipient_id': result.get('recipient_id', ''),
            'action_token': result.get('action_token', ''),
            'enviado_em': datetime.now(timezone.utc).isoformat(),
            'atualizado_em': datetime.now(timezone.utc).isoformat()
        }
        envelopes = load_envelopes()
        envelopes.append(envelope_record)
        save_envelopes(envelopes)

        # Adicionar evento na timeline do paciente
        add_timeline_event(
            paciente_id, 'documento',
            f'Documento enviado para assinatura',
            f'{doc_titulo} enviado via {canal} para {result.get("enviado_para", "")}'
        )

        logger.info(f"✅ Intellisign: {doc_titulo} enviado para {pac_nome} via {canal}")

        return jsonify({
            'success': True,
            'envelope_id': result.get('envelope_id', ''),
            'message': f'Documento enviado para assinatura via {canal}',
            'enviado_para': result.get('enviado_para', '')
        })

    except Exception as e:
        logger.error(f"Intellisign erro: {e}")
        return jsonify({'error': f'Erro ao enviar documento: {str(e)}'}), 500


@app.route('/api/intellisign/envelopes', methods=['GET'])
def intellisign_listar():
    """Lista todos os envelopes de assinatura salvos localmente."""
    paciente_id = request.args.get('paciente_id')
    envelopes = load_envelopes()
    if paciente_id:
        envelopes = [e for e in envelopes if e.get('paciente_id') == paciente_id]
    return jsonify(envelopes)


@app.route('/api/intellisign/envelope/<envelope_id>', methods=['GET'])
def intellisign_status(envelope_id):
    """Consulta status de um envelope na API Intellisign e atualiza local."""
    envelopes = load_envelopes()
    env_local = next((e for e in envelopes if e.get('id') == envelope_id), None)

    if intellisign and intellisign.is_configured():
        try:
            remote = intellisign.get_envelope(envelope_id, extended=True)
            if 'error' not in remote:
                new_state = remote.get('state', '')
                # Atualizar registro local
                if env_local:
                    env_local['status'] = new_state
                    env_local['atualizado_em'] = datetime.now(timezone.utc).isoformat()
                    if new_state == 'completed':
                        env_local['assinado_em'] = datetime.now(timezone.utc).isoformat()
                    save_envelopes(envelopes)
                return jsonify({
                    'envelope': remote,
                    'local': env_local
                })
        except Exception as e:
            logger.error(f"Erro ao consultar Intellisign: {e}")

    if env_local:
        return jsonify({'envelope': env_local, 'local': env_local})

    return jsonify({'error': 'Envelope não encontrado'}), 404


@app.route('/api/intellisign/reenviar/<envelope_id>', methods=['POST'])
def intellisign_reenviar(envelope_id):
    """Reenvia notificação ao paciente."""
    if not intellisign or not intellisign.is_configured():
        return jsonify({'error': 'Intellisign não configurado'}), 503

    try:
        result = intellisign.renotify_envelope(envelope_id)
        if result.get('success'):
            return jsonify({'success': True, 'message': 'Notificação reenviada ao paciente'})
        return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/intellisign/cancelar/<envelope_id>', methods=['POST'])
def intellisign_cancelar(envelope_id):
    """Cancela um envelope pendente."""
    if not intellisign or not intellisign.is_configured():
        return jsonify({'error': 'Intellisign não configurado'}), 503

    try:
        result = intellisign.cancel_envelope(envelope_id)
        if result.get('success'):
            envelopes = load_envelopes()
            for e in envelopes:
                if e.get('id') == envelope_id:
                    e['status'] = 'cancelled'
                    e['atualizado_em'] = datetime.now(timezone.utc).isoformat()
            save_envelopes(envelopes)
            return jsonify({'success': True, 'message': 'Envelope cancelado'})
        return jsonify(result), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/intellisign/download/<envelope_id>', methods=['GET'])
def intellisign_download(envelope_id):
    """Download do documento assinado."""
    if not intellisign or not intellisign.is_configured():
        return jsonify({'error': 'Intellisign não configurado'}), 503

    try:
        content = intellisign.download_envelope(envelope_id)
        if content:
            from flask import send_file
            from io import BytesIO
            return send_file(
                BytesIO(content),
                mimetype='application/zip',
                as_attachment=True,
                download_name=f'envelope_{envelope_id[:8]}_assinado.zip'
            )
        return jsonify({'error': 'Erro ao baixar documento'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== CANNABIS MEDICINAL MODULE =====
try:
    from cannabis_api import cannabis_bp
    app.register_blueprint(cannabis_bp)
    logger.info("✅ Módulo Cannabis Medicinal registrado com sucesso")
except ImportError as e:
    logger.warning(f"⚠️ Cannabis Medicinal não disponível: {e}")
except Exception as e:
    logger.error(f"❌ Erro ao registrar Cannabis Medicinal: {e}")


ensure_db_ready()


if __name__ == "__main__":
    init_db()
    seed_admin()
    app.run(debug=True, use_reloader=True, host='0.0.0.0', port=5000)

