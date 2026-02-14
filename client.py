import requests

url = "http://127.0.0.1:8000/login"
data = {"client_id": "m", "password": "123"}

resp = requests.post(url, json=data)

print("Status:", resp.status_code)
print("Response:", resp.json())
