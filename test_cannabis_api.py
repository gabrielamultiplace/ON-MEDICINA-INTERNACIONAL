#!/usr/bin/env python
"""Test cannabis API endpoints."""

import requests
import json
import time

BASE_URL = 'http://localhost:5000/api/cannabis'

def test_health():
    """Test health check endpoint."""
    print("\n=== TEST 1: Health Check ===")
    try:
        r = requests.get(f'{BASE_URL}/health', timeout=5)
        print(f'Status: {r.status_code}')
        print(f'Content-Type: {r.headers.get("content-type")}')
        print(f'Response: {r.text[:500]}')
        if r.status_code == 200:
            print('✅ Health check passed')
            return True
    except Exception as e:
        print(f'❌ Error: {e}')
    return False

def test_products():
    """Test products list endpoint."""
    print("\n=== TEST 2: Get Products ===")
    try:
        r = requests.get(f'{BASE_URL}/products', timeout=5)
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            print(f'✅ Got {len(data.get("products", []))} products')
            return True
    except Exception as e:
        print(f'❌ Error: {e}')
    return False

def test_prescription_calculate():
    """Test prescription calculation."""
    print("\n=== TEST 3: Calculate Prescription ===")
    try:
        payload = {
            'product_id': 'PROD001',
            'patient_name': 'Test Patient',
            'patient_diagnosis': 'Epilepsy',
            'medical_indication': 'Seizure control'
        }
        r = requests.post(
            f'{BASE_URL}/prescriptions/calculate',
            json=payload,
            timeout=5
        )
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                print(f'✅ Prescription calculated')
                print(f'   - Initial CBD: {data["prescription"]["initial_cbd_mg_daily"]} mg')
                print(f'   - Weeks: {len(data["titulation_weeks"])}')
                print(f'   - Projection: {len(data["projection_24_months"])} months')
                return True
        else:
            print(f'❌ Status {r.status_code}: {r.text[:200]}')
    except Exception as e:
        print(f'❌ Error: {e}')
    return False

if __name__ == '__main__':
    print('\n🔬 CANNABIS API TEST SUITE')
    print('=' * 50)
    
    print('Waiting for server...')
    time.sleep(2)
    
    results = []
    results.append(('Health', test_health()))
    results.append(('Products', test_products()))
    results.append(('Calculate', test_prescription_calculate()))
    
    print('\n' + '=' * 50)
    print('📊 RESULTS:')
    for name, passed in results:
        status = '✅ PASS' if passed else '❌ FAIL'
        print(f'  {status} - {name}')
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f'\nTotal: {passed}/{total} tests passed')
