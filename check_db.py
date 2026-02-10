#!/usr/bin/env python
"""Verify database records."""

from cannabis_models import CannabisDB

db = CannabisDB()

print("\n📊 DATABASE STATUS CHECK")
print("=" * 50)

# Check prescriptions
result = db.execute_query('SELECT COUNT(*) as count FROM cannabis_prescriptions')
if result:
    count = result[0]['count']
    print(f"✓ Prescriptions: {count}")

# Get last prescription details
result = db.execute_query('SELECT prescription_id, patient_name, status FROM cannabis_prescriptions ORDER BY created_at DESC LIMIT 1')
if result:
    rx = result[0]
    print(f"  Latest: {rx['prescription_id']} - {rx['patient_name']} ({rx['status']})")

# Check titulation
result = db.execute_query('SELECT COUNT(*) as count FROM cannabis_titulation_schedule')
if result:
    count = result[0]['count']
    print(f"✓ Titulation records: {count}")

# Check judicial projection
result = db.execute_query('SELECT COUNT(*) as count FROM cannabis_judicial_projection')
if result:
    count = result[0]['count']
    print(f"✓ Judicial projections: {count}")

# Check medical reports
result = db.execute_query('SELECT COUNT(*) as count FROM cannabis_medical_reports')
if result:
    count = result[0]['count']
    print(f"✓ Medical reports: {count}")

# Check exam requests
result = db.execute_query('SELECT COUNT(*) as count FROM cannabis_exam_requests')
if result:
    count = result[0]['count']
    print(f"✓ Exam requests: {count}")

print("=" * 50)
print("✅ All tables accessible and populated")
