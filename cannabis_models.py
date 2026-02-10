"""
CANNABIS MEDICINAL - DATABASE MODELS & SCHEMA
==============================================
SQLite3 tables for products, suppliers, prescriptions, exams, judicial records.
"""

from datetime import datetime
from typing import List, Dict, Optional
import json
import sqlite3


# SQL CREATE STATEMENTS
CANNABIS_SCHEMA = """
-- ============ SUPPLIERS ============
CREATE TABLE IF NOT EXISTS cannabis_suppliers (
    supplier_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    cnpj TEXT UNIQUE,
    contact_email TEXT,
    contact_phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT DEFAULT 'Brasil',
    anvisa_authorized INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============ CANNABIS PRODUCTS ============
CREATE TABLE IF NOT EXISTS cannabis_products (
    product_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    description TEXT,
    cbd_mg_ml REAL NOT NULL,
    thc_mg_ml REAL NOT NULL,
    volume_ml INTEGER NOT NULL,
    batch_number TEXT,
    manufacturing_date DATE,
    expiry_date DATE,
    anvisa_registration TEXT,
    product_type TEXT,  -- 'Isolate', 'Full Spectrum', 'Broad Spectrum'
    storage_conditions TEXT,
    price_brl REAL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(supplier_id) REFERENCES cannabis_suppliers(supplier_id)
);

-- ============ PRESCRIPTIONS ============
CREATE TABLE IF NOT EXISTS cannabis_prescriptions (
    prescription_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    consultation_id TEXT,
    
    -- Medical info
    diagnosis TEXT NOT NULL,
    medical_indication TEXT NOT NULL,
    clinical_notes TEXT,
    
    -- Dosage
    initial_cbd_mg_daily REAL,
    initial_thc_mg_daily REAL,
    frequency TEXT,  -- e.g., "2 GOTAS DE 12 EM 12 HORAS"
    drops_per_dose INTEGER,
    times_per_day INTEGER,
    
    -- Duration
    duration_months INTEGER DEFAULT 24,  -- Judicial requirement
    titulation_required INTEGER DEFAULT 1,
    
    -- Digital signatures
    doctor_signature_url TEXT,
    doctor_signature_date TIMESTAMP,
    signature_provider TEXT,  -- 'VidaaS', 'DocuSign', etc.
    
    -- Status
    status TEXT DEFAULT 'draft',  -- 'draft', 'signed', 'active', 'cancelled'
    is_judicial_case INTEGER DEFAULT 1,  -- Required for judicial defense
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signed_at TIMESTAMP,
    
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES users(user_id),
    FOREIGN KEY(product_id) REFERENCES cannabis_products(product_id),
    FOREIGN KEY(consultation_id) REFERENCES consultations(consultation_id)
);

-- ============ TITULATION SCHEDULE (24 WEEKS OF PROGRESSION) ============
CREATE TABLE IF NOT EXISTS cannabis_titulation_schedule (
    schedule_id TEXT PRIMARY KEY,
    prescription_id TEXT NOT NULL,
    week_number INTEGER NOT NULL,
    drops_per_dose INTEGER,
    times_per_day INTEGER,
    frequency_text TEXT,
    cbd_mg_per_dose REAL,
    cbd_mg_per_day REAL,
    cbd_mg_per_week REAL,
    thc_mg_per_day REAL,
    start_date DATE,
    end_date DATE,
    therapeutic_goal TEXT,
    
    FOREIGN KEY(prescription_id) REFERENCES cannabis_prescriptions(prescription_id)
);

-- ============ 24-MONTH JUDICIAL PROJECTION ============
CREATE TABLE IF NOT EXISTS cannabis_judicial_projection (
    projection_id TEXT PRIMARY KEY,
    prescription_id TEXT NOT NULL,
    month_number INTEGER,
    projected_date DATE,
    titulation_week INTEGER,
    cbd_mg_daily REAL,
    cbd_mg_monthly REAL,
    cbd_mg_cumulative REAL,
    ml_per_month REAL,
    bottles_needed REAL,
    monthly_cost_brl REAL,
    cumulative_cost_brl REAL,
    therapeutic_goal TEXT,
    
    FOREIGN KEY(prescription_id) REFERENCES cannabis_prescriptions(prescription_id)
);

-- ============ MEDICAL REPORTS (LAUDOS) ============
CREATE TABLE IF NOT EXISTS cannabis_medical_reports (
    report_id TEXT PRIMARY KEY,
    prescription_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    
    -- Report info
    report_type TEXT,  -- 'Inicial', 'Progressão', 'Manutenção', 'Alta'
    clinical_findings TEXT,
    therapeutic_response TEXT,
    side_effects TEXT,
    adjustments_made TEXT,
    
    -- Legal info for court
    for_judicial_defense INTEGER DEFAULT 1,
    legal_arguments TEXT,
    supporting_evidence TEXT,
    
    -- Signatures
    doctor_signature_url TEXT,
    doctor_signature_date TIMESTAMP,
    signature_provider TEXT,
    
    -- Status
    status TEXT DEFAULT 'draft',  -- 'draft', 'signed', 'finalized'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signed_at TIMESTAMP,
    
    FOREIGN KEY(prescription_id) REFERENCES cannabis_prescriptions(prescription_id),
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES users(user_id)
);

-- ============ EXAM REQUESTS ============
CREATE TABLE IF NOT EXISTS cannabis_exam_requests (
    exam_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    prescription_id TEXT,
    
    -- Exam type
    exam_type TEXT NOT NULL,  -- 'Laboratorial', 'Genético'
    exam_name TEXT,
    description TEXT,
    
    -- Exam items
    exam_items TEXT,  -- JSON: ["Ácido Fólico", "Glicose", "Hemograma", ...]
    
    -- Request details
    clinical_reason TEXT,
    urgency TEXT DEFAULT 'Normal',  -- 'Urgente', 'Normal'
    
    -- Digital signature
    doctor_signature_url TEXT,
    doctor_signature_date TIMESTAMP,
    signature_provider TEXT,  -- 'VidaaS', 'DocuSign', etc.
    
    -- Status
    status TEXT DEFAULT 'requested',  -- 'requested', 'signed', 'sent_to_lab', 'completed'
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signed_at TIMESTAMP,
    
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES users(user_id),
    FOREIGN KEY(prescription_id) REFERENCES cannabis_prescriptions(prescription_id)
);

-- ============ EXAM RESULTS STORAGE ============
CREATE TABLE IF NOT EXISTS cannabis_exam_results (
    result_id TEXT PRIMARY KEY,
    exam_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    
    exam_pdf_url TEXT,
    lab_name TEXT,
    result_date DATE,
    observations TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(exam_id) REFERENCES cannabis_exam_requests(exam_id),
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
);

-- ============ PATIENT EXAM CONTAINER ============
CREATE TABLE IF NOT EXISTS cannabis_patient_exams (
    container_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL UNIQUE,
    
    -- Exam tracking
    total_exams_requested INTEGER DEFAULT 0,
    total_exams_completed INTEGER DEFAULT 0,
    
    -- Active prescription
    active_prescription_id TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_exam_date TIMESTAMP,
    
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(active_prescription_id) REFERENCES cannabis_prescriptions(prescription_id)
);

-- ============ PRESCRIPTION-EXAM RELATIONSHIP ============
CREATE TABLE IF NOT EXISTS cannabis_prescription_exams (
    relationship_id TEXT PRIMARY KEY,
    prescription_id TEXT NOT NULL,
    exam_id TEXT NOT NULL,
    reason TEXT,  -- 'baseline', 'monitoring', 'follow_up'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(prescription_id) REFERENCES cannabis_prescriptions(prescription_id),
    FOREIGN KEY(exam_id) REFERENCES cannabis_exam_requests(exam_id)
);

-- ============ INDICES FOR PERFORMANCE ============
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON cannabis_prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_doctor ON cannabis_prescriptions(doctor_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_status ON cannabis_prescriptions(status);
CREATE INDEX IF NOT EXISTS idx_prescriptions_product ON cannabis_prescriptions(product_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON cannabis_products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_exams_patient ON cannabis_exam_requests(patient_id);
CREATE INDEX IF NOT EXISTS idx_exams_prescription ON cannabis_exam_requests(prescription_id);
CREATE INDEX IF NOT EXISTS idx_reports_prescription ON cannabis_medical_reports(prescription_id);
CREATE INDEX IF NOT EXISTS idx_reports_patient ON cannabis_medical_reports(patient_id);
"""


class CannabisDB:
    """Database helper for cannabis module."""
    
    def __init__(self, db_path: str = 'data.db'):
        self.db_path = db_path
        self.init_schema()
    
    def init_schema(self):
        """Initialize cannabis tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Split and execute each CREATE TABLE statement
        statements = CANNABIS_SCHEMA.split(';')
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                except sqlite3.OperationalError as e:
                    if 'already exists' not in str(e):
                        print(f"Error: {e}")
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SELECT query and return results as list of dicts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def execute_insert(self, query: str, params: tuple = ()) -> str:
        """Execute INSERT and return last_row_id."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        conn.commit()
        row_id = cursor.lastrowid
        
        conn.close()
        return row_id
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute UPDATE and return rows affected."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        conn.commit()
        rows_affected = cursor.rowcount
        
        conn.close()
        return rows_affected


# Seed data
SEED_SUPPLIERS = [
    {
        'supplier_id': 'SUP001',
        'name': 'Principios Ativos Cannabis',
        'cnpj': '12.345.678/0001-90',
        'contact_email': 'contato@principios.com.br',
        'contact_phone': '(11) 99999-9999',
        'city': 'São Paulo',
        'state': 'SP',
        'anvisa_authorized': 1
    },
    {
        'supplier_id': 'SUP002',
        'name': 'Cannabis Medicinal Brasil',
        'cnpj': '98.765.432/0001-10',
        'contact_email': 'vendas@cannabismedicinal.br',
        'contact_phone': '(21) 98888-8888',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'anvisa_authorized': 1
    }
]

SEED_PRODUCTS = [
    {
        'product_id': 'PROD001',
        'supplier_id': 'SUP001',
        'name': 'CBD Isolate USA Hemp',
        'brand': 'Principios Ativos',
        'description': 'Pure CBD isolate derived from USA hemp',
        'cbd_mg_ml': 10.0,
        'thc_mg_ml': 0.0,
        'volume_ml': 30,
        'product_type': 'Isolate',
        'price_brl': 150.00,
        'anvisa_registration': 'ANVISA-001'
    },
    {
        'product_id': 'PROD002',
        'supplier_id': 'SUP001',
        'name': 'CBD Tincture - Full Spectrum',
        'brand': 'Principios Ativos',
        'description': 'Full spectrum CBD tincture with minor cannabinoids',
        'cbd_mg_ml': 8.0,
        'thc_mg_ml': 0.3,
        'volume_ml': 30,
        'product_type': 'Full Spectrum',
        'price_brl': 180.00,
        'anvisa_registration': 'ANVISA-002'
    },
    {
        'product_id': 'PROD003',
        'supplier_id': 'SUP002',
        'name': 'CBD:THC 1:1 Balance',
        'brand': 'Cannabis Medicinal Brasil',
        'description': 'Balanced CBD:THC 1:1 ratio for therapeutic relief',
        'cbd_mg_ml': 5.0,
        'thc_mg_ml': 5.0,
        'volume_ml': 30,
        'product_type': 'Full Spectrum',
        'price_brl': 200.00,
        'anvisa_registration': 'ANVISA-003'
    }
]
