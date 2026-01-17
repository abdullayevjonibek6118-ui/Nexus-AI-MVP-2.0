
import requests
import sys

try:
    # Login first to get token
    login_resp = requests.post(
        "http://localhost:8000/api/auth/login", 
        data={"username": "jonithe20@gmail.com", "password": "Password123!"}
    )
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        sys.exit(1)
        
    token = login_resp.json()["access_token"]
    
    # Get Analytics
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get("http://localhost:8000/api/analytics/", headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print("KEYS:", data.keys())
        if "metrics" in data:
            print("METRICS:", data["metrics"])
        else:
            print("ERROR: 'metrics' key missing in response")
    else:
        print(f"Analytics API Failed: {resp.status_code} - {resp.text}")

except Exception as e:
    print(f"Error: {e}")
