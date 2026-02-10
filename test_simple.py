import requests
import sys

print("Testing cannabis health endpoint...")
try:
    r = requests.get('http://127.0.0.1:5000/api/cannabis/health', timeout=5)
    print(f'Status Code: {r.status_code}')
    print(f'URL: {r.url}')
    print(f'Response Text: {r.text[:500]}')
    if r.status_code == 200:
        print(f'JSON: {r.json()}')
        print("✅ SUCCESS")
        sys.exit(0)
    else:
        print("❌ FAILED")
        sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
