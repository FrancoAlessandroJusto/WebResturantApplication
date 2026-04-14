#!/usr/bin/env python3
import requests
import json

def test_menu_api():
    try:
        # Test GET menu items
        response = requests.get("http://127.0.0.1:8000/menu")
        print(f"GET /menu status: {response.status_code}")
        
        if response.status_code == 200:
            items = response.json()
            print(f"Menu items trovati: {len(items)}")
            if items:
                print("Primo item:")
                print(json.dumps(items[0], indent=2))
        else:
            print(f"Errore GET: {response.text}")
        
        # Test GET ingredienti
        response = requests.get("http://127.0.0.1:8000/ingredienti")
        print(f"\nGET /ingredienti status: {response.status_code}")
        
        if response.status_code == 200:
            ingredienti = response.json()
            print(f"Ingredienti trovati: {len(ingredienti)}")
            if ingredienti:
                print("Primi 3 ingredienti:")
                for ing in ingredienti[:3]:
                    print(f"  - {ing['nome']} (ID: {ing['id']}, Tipo: {ing['tipo']})")
        else:
            print(f"Errore GET ingredienti: {response.text}")
        
        # Test POST nuovo menu item
        new_item_data = {
            "nome": "Pizza Test API",
            "prezzo": 12.50,
            "categoria": "Pizza",
            "ingredienti": [
                {"ingrediente_id": 43, "quantita": 0.2},  # Pomodoro San Marzano
                {"ingrediente_id": 45, "quantita": 0.15}  # Parmigiano Reggiano
            ]
        }
        
        response = requests.post("http://127.0.0.1:8000/menu", json=new_item_data)
        print(f"\nPOST /menu status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Item creato con successo:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Errore POST: {response.text}")
            
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    test_menu_api()
