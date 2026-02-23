
import requests

BASE_URL = "http://localhost:8000/api"

def test_dashboard():
    # Login
    login_data = {"email": "admin@cdss.gov.in", "password": "admin123"}
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if r.status_code != 200:
        print(f"Login failed: {r.status_code}")
        print(r.text)
        return
    
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test children
    print("\nTesting /dashboard/children...")
    r = requests.get(f"{BASE_URL}/dashboard/children?lang=te", headers=headers)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        children = r.json()
        print(f"Count: {len(children)}")
        if children:
            print(f"First child localized gender: {children[0].get('gender')}")
    else:
        print(r.text)

    # Test interventions
    print("\nTesting /dashboard/interventions...")
    r = requests.get(f"{BASE_URL}/dashboard/interventions?lang=te", headers=headers)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        intvs = r.json()
        print(f"Count: {len(intvs)}")
    else:
        print(r.text)

if __name__ == "__main__":
    test_dashboard()
