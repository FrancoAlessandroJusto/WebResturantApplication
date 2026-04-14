#!/usr/bin/env python3
import requests
import json

def test_menu_creation():
    try:
        # Test creazione menu item completo
        new_item_data = {
            "nome": "Pizza Test Completata",
            "prezzo": 15.50,
            "categoria": "Pizza",
            "ingredienti": [
                {"ingrediente_id": 43, "quantita": 0.2},  # Pomodoro San Marzano
                {"ingrediente_id": 45, "quantita": 0.15}, # Parmigiano Reggiano
                {"ingrediente_id": 48, "quantita": 0.2}  # Bufala Campana DOP
            ]
        }
        
        print("Testing menu creation with ingredients...")
        response = requests.post("http://127.0.0.1:8000/menu", json=new_item_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Item created successfully!")
            print(f"Item ID: {result.get('id')}")
            print(f"Name: {result.get('nome')}")
            print(f"Price: €{result.get('prezzo')}")
            print(f"Category: {result.get('categoria')}")
            print(f"Ingredients: {len(result.get('ingredienti', []))}")
        else:
            print("❌ ERROR:")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_menu_creation()
