import requests

BASE_URL = "http://localhost:8000/api"

def test_redirect_bug():
    print("--- Testing Login ---")
    login_data = {"email": "admin@cdss.gov.in", "password": "admin123"}
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        response.raise_for_status()
        token = response.json()["access_token"]
        print("✓ Login successful")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}
    session = requests.Session()
    session.headers.update(headers)

    print("\n--- Testing /children (NO trailing slash) ---")
    resp = session.get(f"{BASE_URL}/children", allow_redirects=False)
    print(f"Response status: {resp.status_code}")
    if resp.status_code == 200:
        print("✓ Access successful (no redirect)")
    elif resp.status_code in [301, 302, 307, 308]:
        print(f"! Redirected to: {resp.headers.get('Location')}")
    else:
        print(f"✗ Failed: {resp.status_code}")
        print(f"Detail: {resp.text}")

    print("\n--- Testing /referrals (NO trailing slash) ---")
    resp_ref = session.get(f"{BASE_URL}/referrals", allow_redirects=False)
    print(f"Response status: {resp_ref.status_code}")
    if resp_ref.status_code == 200:
        print("✓ Access successful (no redirect)")
    else:
        print(f"✗ Failed: {resp_ref.status_code}")
        print(f"Detail: {resp_ref.text}")

if __name__ == "__main__":
    test_redirect_bug()
