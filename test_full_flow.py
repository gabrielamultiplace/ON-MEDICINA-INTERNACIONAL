#!/usr/bin/env python
"""Test full cannabis prescription flow via Flask test client."""

from app import app
import json
import os

client = app.test_client()

print("\n" + "="*60)
print("🧬 CANNABIS MEDICINAL - FULL FLOW TEST")
print("="*60)

# TEST 1: Health Check
print("\n[1/4] Health Check...")
response = client.get('/api/cannabis/health')
assert response.status_code == 200, f"Health check failed: {response.status_code}"
print("✅ Health: OPERATIONAL")

# TEST 2: List Products
print("\n[2/4] Get Available Products...")
response = client.get('/api/cannabis/products')
assert response.status_code == 200, f"Products failed: {response.status_code}"
data = response.get_json()
assert data['success'], "Products endpoint failed"
products = data.get('products', [])
print(f"✅ Found {len(products)} products:")
for p in products[:2]:
    print(f"   - {p['name']} (CBD: {p['cbd_mg_ml']} mg/mL, Price: R$ {p['price_brl']})")

# TEST 3: Calculate Prescription
print("\n[3/4] Calculate Prescription (Math Only)...")
payload = {
    'product_id': products[0]['product_id'] if products else 'PROD001',
    'patient_name': 'João Silva',
    'patient_diagnosis': 'Epilepsia',
    'medical_indication': 'Controle de crises'
}
response = client.post(
    '/api/cannabis/prescriptions/calculate',
    json=payload,
    content_type='application/json'
)
assert response.status_code == 200, f"Calculate failed: {response.status_code}"
calc_data = response.get_json()
assert calc_data['success'], "Calculation failed"
print("✅ Prescription Calculated:")
print(f"   - Initial CBD/day: {calc_data['prescription']['initial_cbd_mg_daily']:.1f} mg")
print(f"   - Titulation weeks: {len(calc_data['titulation_weeks'])}")
print(f"   - 24-month projection: {len(calc_data['projection_24_months'])} months")
print(f"   - Total CBD (24m): {calc_data['judicial_summary']['total_cbd_projected_mg']:.0f} mg")
print(f"   - Bottles needed: {calc_data['judicial_summary']['total_bottles_projected']:.0f}")
print(f"   - Total cost: R$ {calc_data['judicial_summary']['total_cost_projected_brl']:.2f}")

# TEST 4: Create Prescription (with PDF generation)
print("\n[4/4] Create Prescription (Full Save + PDFs)...")
create_payload = {
    'product_id': products[0]['product_id'] if products else 'PROD001',
    'patient_id': '12345',
    'patient_name': 'João Silva',
    'patient_diagnosis': 'Epilepsia',
    'medical_indication': 'Controle de crises',
    'doctor_id': 'doc001',
    'doctor_name': 'Dr. Pedro Santos',
    'doctor_crm': '123456-SP'
}
response = client.post(
    '/api/cannabis/prescriptions',
    json=create_payload,
    content_type='application/json'
)

print(f"   Response Status: {response.status_code}")
if response.status_code == 200 or response.status_code == 201:
    create_data = response.get_json()
    if create_data.get('success'):
        print(f"✅ Prescription Created: {create_data.get('prescription_id')}")
        pdfs = create_data.get('pdf_paths', {})
        print(f"   PDFs Generated:")
        for pdf_type, path in pdfs.items():
            if path:
                exists = os.path.exists(path)
                status = "✓" if exists else "✗"
                print(f"      {status} {pdf_type}: {path}")
    else:
        print(f"❌ Error: {create_data.get('message', 'Unknown error')}")
else:
    print(f"❌ Status {response.status_code}")
    print(f"   Response: {response.get_json() if response.content_type == 'application/json' else response.data[:200]}")

print("\n" + "="*60)
print("✅ TEST SUITE COMPLETED")
print("="*60)
