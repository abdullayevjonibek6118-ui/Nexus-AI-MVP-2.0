
import requests

def test_http_login():
    url = "http://localhost:8000/api/auth/login"
    data = {
        "username": "abdullaevjonibek6118@gmail.com",
        "password": "Joni(6118"
    }
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_http_login()
