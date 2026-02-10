"""
CANNABIS MEDICINAL MODULE - FLASK API ENDPOINTS
===============================================
REST API for prescription management, PDF generation, and judicial records.
Integrate with video consultation module and digital signature APIs.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import uuid

from cannabis_math_engine import PrescriptionCalculator, CannabisProduct
from cannabis_models import CannabisDB, SEED_SUPPLIERS, SEED_PRODUCTS
from cannabis_pdf_generator import (
    PrescriptionPDFGenerator, MedicalReportPDFGenerator,
    ExamRequestPDFGenerator, generate_all_pdfs
)

# Create blueprint
cannabis_bp = Blueprint('cannabis', __name__, url_prefix='/api/cannabis')

# Initialize database and calculator
db = CannabisDB()
calculator = PrescriptionCalculator()

# Seed initial products
def seed_products():
    """Load seed products into calculator."""
    for product_data in SEED_PRODUCTS:
        product = CannabisProduct(
            product_id=product_data['product_id'],
            name=product_data['name'],
            brand=product_data['brand'],
            cbd_mg_ml=product_data['cbd_mg_ml'],
            thc_mg_ml=product_data['thc_mg_ml'],
            volume_ml=product_data['volume_ml'],
            supplier_id=product_data['supplier_id']
        )
        calculator.add_product(product)

seed_products()


# ============================================================================
# SUPPLIERS & PRODUCTS ENDPOINTS
# ============================================================================

@cannabis_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    """Get all authorized cannabis suppliers."""
    try:
        suppliers = db.execute_query('SELECT * FROM cannabis_suppliers WHERE is_active = 1')
        return jsonify({'success': True, 'suppliers': suppliers}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cannabis_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    """Create a new supplier."""
    try:
        data = request.json
        supplier_id = f"SUP_{uuid.uuid4().hex[:8]}"
        
        query = """
            INSERT INTO cannabis_suppliers 
            (supplier_id, name, cnpj, contact_email, contact_phone, city, state, anvisa_authorized)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            supplier_id, data['name'], data.get('cnpj'),
            data.get('contact_email'), data.get('contact_phone'),
            data.get('city'), data.get('state'), data.get('anvisa_authorized', 0)
        )
        
        db.execute_insert(query, params)
        return jsonify({'success': True, 'supplier_id': supplier_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cannabis_bp.route('/products', methods=['GET'])
def get_products():
    """Get all available cannabis products."""
    try:
        products = db.execute_query('SELECT * FROM cannabis_products WHERE is_active = 1')
        return jsonify({'success': True, 'products': products}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cannabis_bp.route('/products', methods=['POST'])
def create_product():
    """Register a new cannabis product."""
    try:
        data = request.json
        product_id = f"PROD_{uuid.uuid4().hex[:8]}"
        
        query = """
            INSERT INTO cannabis_products
            (product_id, supplier_id, name, brand, cbd_mg_ml, thc_mg_ml, volume_ml,
             product_type, price_brl, anvisa_registration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            product_id, data['supplier_id'], data['name'], data['brand'],
            data['cbd_mg_ml'], data['thc_mg_ml'], data['volume_ml'],
            data.get('product_type'), data.get('price_brl'), data.get('anvisa_registration')
        )
        
        db.execute_insert(query, params)
        
        # Also add to calculator
        product = CannabisProduct(
            product_id=product_id,
            name=data['name'],
            brand=data['brand'],
            cbd_mg_ml=data['cbd_mg_ml'],
            thc_mg_ml=data['thc_mg_ml'],
            volume_ml=data['volume_ml'],
            supplier_id=data['supplier_id']
        )
        calculator.add_product(product)
        
        return jsonify({'success': True, 'product_id': product_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PRESCRIPTION ENDPOINTS (CORE FUNCTIONALITY)
# ============================================================================

@cannabis_bp.route('/prescriptions/calculate', methods=['POST'])
def calculate_prescription():
    """
    Calculate prescription with titulation schedule and 24-month judicial projection.
    
    Request body:
    {
        "product_id": "PROD001",
        "patient_name": "Murilo Pinheiro Fogaça",
        "patient_diagnosis": "Epilepsy",
        "medical_indication": "Therapeutic control of seizures"
    }
    
    Returns:
    {
        "prescription": {...},
        "titulation_weeks": [...],
        "projection_24_months": [...],
        "judicial_summary": {...}
    }
    """
    try:
        data = request.json
        
        result = calculator.calculate_prescription(
            product_id=data['product_id'],
            patient_name=data['patient_name'],
            patient_diagnosis=data['patient_diagnosis'],
            medical_indication=data['medical_indication']
        )
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'prescription': result['prescription'],
            'titulation_weeks': result['titulation_weeks'],
            'projection_24_months': result['projection_24_months'],
            'judicial_summary': result['judicial_summary']
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cannabis_bp.route('/prescriptions', methods=['POST'])
def create_prescription():
    """
    Create and save a prescription in database.
    Generates PDFs for Rx, Laudo, and Exam Requests.
    """
    try:
        data = request.json
        
        # Calculate prescription
        calc_result = calculator.calculate_prescription(
            product_id=data['product_id'],
            patient_name=data['patient_name'],
            patient_diagnosis=data['patient_diagnosis'],
            medical_indication=data['medical_indication']
        )
        
        if 'error' in calc_result:
            return jsonify({'success': False, 'error': calc_result['error']}), 400
        
        prescription = calc_result['prescription']
        prescription_id = prescription['prescription_id']
        
        # Save prescription to database
        query = """
            INSERT INTO cannabis_prescriptions
            (prescription_id, patient_id, doctor_id, product_id, consultation_id,
             diagnosis, medical_indication, initial_cbd_mg_daily, initial_thc_mg_daily,
             frequency, duration_months, titulation_required, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            prescription_id, data.get('patient_id', 'temp_patient'),
            data.get('doctor_id', 'temp_doctor'), data['product_id'],
            data.get('consultation_id'), prescription['patient_diagnosis'],
            prescription['medical_indication'], prescription['initial_cbd_mg_daily'],
            prescription['initial_thc_mg_daily'], prescription['frequency_initial'],
            prescription['duration_months'], 1, 'draft'
        )
        
        db.execute_insert(query, params)
        
        # Save titulation schedule
        for week in calc_result['titulation_weeks']:
            schedule_id = f"SCHED_{uuid.uuid4().hex[:8]}"
            query = """
                INSERT INTO cannabis_titulation_schedule
                (schedule_id, prescription_id, week_number, drops_per_dose, times_per_day,
                 frequency_text, cbd_mg_per_dose, cbd_mg_per_day, cbd_mg_per_week,
                 thc_mg_per_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                schedule_id, prescription_id, week['week'],
                week['drops_per_dose'], week['times_per_day'],
                week['frequency'], week['cbd_mg_per_dose'],
                week['cbd_mg_per_day'], week['cbd_mg_per_week'],
                week['thc_mg_per_day']
            )
            db.execute_insert(query, params)
        
        # Save judicial projection
        for month in calc_result['projection_24_months']:
            proj_id = f"PROJ_{uuid.uuid4().hex[:8]}"
            query = """
                INSERT INTO cannabis_judicial_projection
                (projection_id, prescription_id, month_number, cbd_mg_daily,
                 cbd_mg_monthly, cbd_mg_cumulative, ml_per_month, bottles_needed,
                 monthly_cost_brl, cumulative_cost_brl, therapeutic_goal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                proj_id, prescription_id, month['month'],
                month['cbd_mg_daily'], month['cbd_mg_monthly'],
                month['cbd_mg_cumulative'], month['ml_per_month'],
                month['bottles_needed'], month['monthly_cost_brl'],
                month['cumulative_cost_brl'], month['therapeutic_goal']
            )
            db.execute_insert(query, params)
        
        # Generate PDFs
        patient_info = {
            'name': prescription['patient_name'],
            'id': data.get('patient_id', 'temp_patient')
        }
        doctor_info = {
            'name': data.get('doctor_name', 'Dr. Hugo Jaime Rodrigues Alvarez'),
            'crm': data.get('doctor_crm', 'CRMSF 22226')
        }
        
        pdf_paths = generate_all_pdfs(
            prescription,
            calc_result['titulation_weeks'],
            patient_info,
            doctor_info,
            data.get('clinical_findings', '')
        )
        
        return jsonify({
            'success': True,
            'prescription_id': prescription_id,
            'status': 'draft',
            'pdf_paths': pdf_paths,
            'titulation_weeks': calc_result['titulation_weeks'],
            'projection_24_months': calc_result['projection_24_months'],
            'judicial_summary': calc_result['judicial_summary']
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cannabis_bp.route('/prescriptions/<prescription_id>', methods=['GET'])
def get_prescription(prescription_id):
    """Get a specific prescription with all details."""
    try:
        # Get prescription
        prescriptions = db.execute_query(
            'SELECT * FROM cannabis_prescriptions WHERE prescription_id = ?',
            (prescription_id,)
        )
        
        if not prescriptions:
            return jsonify({'success': False, 'error': 'Prescription not found'}), 404
        
        prescription = prescriptions[0]
        
        # Get titulation schedule
        titulation = db.execute_query(
            'SELECT * FROM cannabis_titulation_schedule WHERE prescription_id = ? ORDER BY week_number',
            (prescription_id,)
        )
        
        # Get judicial projection
        projection = db.execute_query(
            'SELECT * FROM cannabis_judicial_projection WHERE prescription_id = ? ORDER BY month_number',
            (prescription_id,)
        )
        
        return jsonify({
            'success': True,
            'prescription': prescription,
            'titulation': titulation,
            'projection_24_months': projection
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cannabis_bp.route('/prescriptions/<prescription_id>/sign', methods=['POST'])
def sign_prescription(prescription_id):
    """
    Sign prescription with digital signature (VidaaS or other provider).
    
    Request body:
    {
        "signature_provider": "VidaaS",
        "signature_url": "https://vidaas.com/signatures/...",
        "doctor_signature_date": "2026-02-04T15:30:00Z"
    }
    """
    try:
        data = request.json
        
        # Update prescription status
        query = """
            UPDATE cannabis_prescriptions
            SET status = ?, doctor_signature_url = ?, signature_provider = ?, signed_at = ?
            WHERE prescription_id = ?
        """
        params = (
            'signed', data.get('signature_url'),
            data.get('signature_provider'), datetime.now().isoformat(),
            prescription_id
        )
        
        db.execute_update(query, params)
        
        return jsonify({
            'success': True,
            'message': 'Prescription digitally signed',
            'signature_provider': data.get('signature_provider'),
            'status': 'signed'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MEDICAL REPORT (LAUDO) ENDPOINTS
# ============================================================================

@cannabis_bp.route('/reports', methods=['POST'])
def create_medical_report():
    """
    Create medical report (Laudo) for judicial defense.
    
    Request body:
    {
        "prescription_id": "RX-...",
        "patient_id": "...",
        "doctor_id": "...",
        "report_type": "Inicial",
        "clinical_findings": "...",
        "therapeutic_response": "...",
        "side_effects": "...",
        "legal_arguments": "..."
    }
    """
    try:
        data = request.json
        report_id = f"LAUDO_{uuid.uuid4().hex[:8]}"
        
        query = """
            INSERT INTO cannabis_medical_reports
            (report_id, prescription_id, patient_id, doctor_id, report_type,
             clinical_findings, therapeutic_response, side_effects, legal_arguments,
             for_judicial_defense, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            report_id, data['prescription_id'], data['patient_id'], data['doctor_id'],
            data.get('report_type', 'Inicial'), data.get('clinical_findings', ''),
            data.get('therapeutic_response', ''), data.get('side_effects', ''),
            data.get('legal_arguments', ''), 1, 'draft'
        )
        
        db.execute_insert(query, params)
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'status': 'draft'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# EXAM REQUEST ENDPOINTS
# ============================================================================

@cannabis_bp.route('/exams', methods=['POST'])
def create_exam_request():
    """
    Create exam request (Laboratorial or Genético).
    
    Request body:
    {
        "patient_id": "...",
        "doctor_id": "...",
        "prescription_id": "RX-...",
        "exam_type": "Laboratorial" or "Genético",
        "exam_items": ["Ácido Fólico", "Glicose", ...],
        "clinical_reason": "Baseline assessment for cannabis treatment"
    }
    """
    try:
        data = request.json
        exam_id = f"EXAM_{uuid.uuid4().hex[:8]}"
        
        query = """
            INSERT INTO cannabis_exam_requests
            (exam_id, patient_id, doctor_id, prescription_id, exam_type,
             exam_items, clinical_reason, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            exam_id, data['patient_id'], data['doctor_id'],
            data.get('prescription_id'), data['exam_type'],
            json.dumps(data.get('exam_items', [])),
            data.get('clinical_reason', ''), 'requested'
        )
        
        db.execute_insert(query, params)
        
        return jsonify({
            'success': True,
            'exam_id': exam_id,
            'status': 'requested'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cannabis_bp.route('/exams/<exam_id>/sign', methods=['POST'])
def sign_exam_request(exam_id):
    """
    Sign exam request with digital signature.
    """
    try:
        data = request.json
        
        query = """
            UPDATE cannabis_exam_requests
            SET status = ?, doctor_signature_url = ?, signature_provider = ?, signed_at = ?
            WHERE exam_id = ?
        """
        params = (
            'signed', data.get('signature_url'),
            data.get('signature_provider'), datetime.now().isoformat(),
            exam_id
        )
        
        db.execute_update(query, params)
        
        return jsonify({
            'success': True,
            'exam_id': exam_id,
            'status': 'signed'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PATIENT EXAM CONTAINER ENDPOINTS
# ============================================================================

@cannabis_bp.route('/patient-exams/<patient_id>', methods=['GET'])
def get_patient_exam_container(patient_id):
    """Get patient's exam container with all associated exams."""
    try:
        # Get or create container
        containers = db.execute_query(
            'SELECT * FROM cannabis_patient_exams WHERE patient_id = ?',
            (patient_id,)
        )
        
        if not containers:
            container_id = f"CONT_{uuid.uuid4().hex[:8]}"
            query = """
                INSERT INTO cannabis_patient_exams (container_id, patient_id)
                VALUES (?, ?)
            """
            db.execute_insert(query, (container_id, patient_id))
            containers = [{'container_id': container_id, 'patient_id': patient_id}]
        
        container = containers[0]
        
        # Get all exams for patient
        exams = db.execute_query(
            'SELECT * FROM cannabis_exam_requests WHERE patient_id = ? ORDER BY created_at DESC',
            (patient_id,)
        )
        
        return jsonify({
            'success': True,
            'container': container,
            'exams': exams
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ANALYTICS & DASHBOARD ENDPOINTS
# ============================================================================

@cannabis_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get cannabis module statistics for dashboard."""
    try:
        total_prescriptions = db.execute_query(
            'SELECT COUNT(*) as count FROM cannabis_prescriptions'
        )[0]['count']
        
        active_prescriptions = db.execute_query(
            "SELECT COUNT(*) as count FROM cannabis_prescriptions WHERE status = 'active'"
        )[0]['count']
        
        judicial_cases = db.execute_query(
            'SELECT COUNT(*) as count FROM cannabis_prescriptions WHERE is_judicial_case = 1'
        )[0]['count']
        
        total_exams = db.execute_query(
            'SELECT COUNT(*) as count FROM cannabis_exam_requests'
        )[0]['count']
        
        return jsonify({
            'success': True,
            'stats': {
                'total_prescriptions': total_prescriptions,
                'active_prescriptions': active_prescriptions,
                'judicial_cases': judicial_cases,
                'total_exams': total_exams
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@cannabis_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for cannabis module."""
    return jsonify({
        'success': True,
        'module': 'cannabis_medicinal',
        'status': 'operational',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200
