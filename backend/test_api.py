import httpx
import json

base_url = "http://127.0.0.1:8000/api/v1/auth"

def test_api():
    print("--- 1. Probando Registro ---")
    data = {
        "email": "bot@academix.com",
        "password": "mypassword123",
        "first_name": "Bot",
        "last_name": "Tester",
        "student_type": "high_school",
        "institution_name": "Academia Virtual"
    }
    r = httpx.post(f"{base_url}/register", json=data)
    print("Status:", r.status_code)
    print("Respuesta:", r.text)

    print("\n--- 2. Probando Login ---")
    form_data = {
        "username": "bot@academix.com",
        "password": "mypassword123"
    }
    r2 = httpx.post(f"{base_url}/login", data=form_data)
    print("Status:", r2.status_code)
    print("Respuesta:", r2.text)
    
    if r2.status_code == 200:
        token = r2.json().get("access_token")
        print("\n--- 3. Probando Perfil Protegido (/me) ---")
        headers = {"Authorization": f"Bearer {token}"}
        r3 = httpx.get(f"{base_url}/me", headers=headers)
        print("Status:", r3.status_code)
        print("Respuesta Pefil:\n", json.dumps(r3.json(), indent=2))

if __name__ == "__main__":
    test_api()
