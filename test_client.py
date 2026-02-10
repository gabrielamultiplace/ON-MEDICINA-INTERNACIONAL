#!/usr/bin/env python
"""Test using Flask test client."""

from app import app

client = app.test_client()

print("Testing with Flask test client...")

# Test health endpoint
response = client.get('/api/cannabis/health')
print(f"Status: {response.status_code}")
print(f"Data: {response.get_json() if response.status_code == 200 else response.data[:200]}")

if response.status_code == 200:
    print("✅ SUCCESS!")
else:
    print("❌ FAILED")
    # List all routes
    print("\nAll registered routes containing 'cannabis':")
    for rule in app.url_map.iter_rules():
        if 'cannabis' in rule.rule:
            print(f"  {rule.rule} [{','.join(rule.methods - {'OPTIONS', 'HEAD'})}] -> {rule.endpoint}")
