import requests

BASE = "http://localhost:8000/api"

# Login as a parent
resp = requests.post(f"{BASE}/auth/login", json={
    "email": "parent_1@gmail.com",
    "password": "test123"
})
print(f"Login status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Login body: {resp.text}")
    exit(1)

token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 1. GET /dashboard/children
print("\n--- GET /dashboard/children ---")
r = requests.get(f"{BASE}/dashboard/children", headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Children count: {len(data)}")
    if data:
        print(f"First child: {data[0]}")
else:
    print(f"Error: {r.text[:500]}")

# 2. GET /dashboard/interventions
print("\n--- GET /dashboard/interventions ---")
r = requests.get(f"{BASE}/dashboard/interventions", headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Interventions count: {len(data)}")
else:
    print(f"Error: {r.text[:500]}")

# 3. GET /dashboard/child-growth/{child_id}
if r.status_code == 200 or True:
    # Get child_id from children endpoint
    children_r = requests.get(f"{BASE}/dashboard/children", headers=headers)
    if children_r.status_code == 200 and children_r.json():
        child_id = children_r.json()[0]["child_id"]
        print(f"\n--- GET /dashboard/child-growth/{child_id} ---")
        r = requests.get(f"{BASE}/dashboard/child-growth/{child_id}", headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Child name: {data.get('child_name')}")
            print(f"Datapoints: {len(data.get('datapoints', []))}")
            print(f"Has prediction: {data.get('latest_prediction') is not None}")
        else:
            print(f"Error: {r.text[:500]}")
    else:
        print("\nSkipping child-growth test - no children returned")
