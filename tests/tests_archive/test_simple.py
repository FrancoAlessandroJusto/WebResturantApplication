#!/usr/bin/env python3
import requests

def test_simple():
    try:
        response = requests.post("http://127.0.0.1:8000/menu", json={
            "nome": "Test Simple",
            "prezzo": 10.0,
            "categoria": "Pizza",
            "ingredienti": []
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple()
