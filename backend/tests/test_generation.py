import requests
import json
import time
import sys

def test_generate_endpoint():
    url = "http://127.0.0.1:8080/api/generate"
    payload = {
        "title": "150 Aniversario de la Universidad",
        "body": "La universidad celebra su 150 aniversario con una serie de eventos académicos y culturales. Invitamos a toda la comunidad a participar.",
        "platforms": ["facebook", "instagram"]
    }
    
    print(f"Testing {url} with payload: {payload}")
    
    try:
        # We might need to wait for server to start if running in CI/CD, but here we assume it's running or we'll handle connection error
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            print("Success! Response:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"Failed with status {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Connection refused. Is the server running?")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_generate_endpoint()
    if not success:
        sys.exit(1)
