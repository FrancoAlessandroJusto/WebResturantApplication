#!/usr/bin/env python3
"""
Test per verificare il funzionamento delle modifiche ingredienti
"""

import requests
import json

def test_price_rules():
    """Test delle regole prezzo"""
    print("Test regole prezzo...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/orders/price-rules")
        print(f"GET /api/v1/orders/price-rules status: {response.status_code}")
        
        if response.status_code == 200:
            rules = response.json()
            print("Regole prezzo trovate:")
            for tipo, prezzi in rules.items():
                print(f"  {tipo}: +{prezzi['aggiunta']}€ / -{prezzi['rimozione']}€")
            return True
        else:
            print(f"Errore: {response.text}")
            return False
            
    except Exception as e:
        print(f"Errore: {e}")
        return False

def test_ingredients_endpoint():
    """Test endpoint ingredienti per un item"""
    print("\nTest endpoint ingredienti...")
    
    try:
        # Prima ottieni ordini attivi
        response = requests.get("http://127.0.0.1:8000/orders")
        if response.status_code != 200:
            print("Nessun ordine attivo trovato")
            return False
            
        orders = response.json()
        if not orders:
            print("Nessun ordine attivo")
            return False
        
        order = orders[0]
        order_id = order["id"]
        
        if not order["dettagli"]:
            print("Ordine senza dettagli")
            return False
        
        # Prende il primo item
        first_item = order["dettagli"][0]
        pizza_id = first_item["pizza_id"]
        
        print(f"Testando item {pizza_id} dell'ordine {order_id}")
        
        # Test endpoint ingredienti
        response = requests.get(f"http://127.0.0.1:8000/api/v1/orders/{order_id}/items/{pizza_id}/ingredients")
        print(f"GET /api/v1/orders/{order_id}/items/{pizza_id}/ingredients status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Item ID: {data['item_id']}")
            print(f"Prezzo base: €{data['prezzo_base']}")
            print(f"Prezzo personalizzato: €{data['prezzo_personalizzato']}")
            print(f"Ingredienti attuali: {len(data['current_ingredients'])}")
            print(f"Ingredienti disponibili: {len(data['available_ingredients'])}")
            return True
        else:
            print(f"Errore: {response.text}")
            return False
            
    except Exception as e:
        print(f"Errore: {e}")
        return False

def test_modify_ingredients():
    """Test modifica ingredienti"""
    print("\nTest modifica ingredienti...")
    
    try:
        # Ottieni ordini attivi
        response = requests.get("http://127.0.0.1:8000/orders")
        if response.status_code != 200:
            return False
            
        orders = response.json()
        if not orders:
            return False
        
        order = orders[0]
        order_id = order["id"]
        first_item = order["dettagli"][0]
        pizza_id = first_item["pizza_id"]
        
        # Test modifica (aggiunta e rimozione)
        modify_data = {
            "added_ingredients": [1, 2],  # ID ingredienti da aggiungere
            "removed_ingredients": [3, 4]  # ID ingredienti da rimuovere
        }
        
        response = requests.post(
            f"http://127.0.0.1:8000/api/v1/orders/{order_id}/items/{pizza_id}/modify",
            json=modify_data
        )
        print(f"POST /api/v1/orders/{order_id}/items/{pizza_id}/modify status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Prezzo base: €{result['prezzo_base']}")
            print(f"Prezzo personalizzato: €{result['prezzo_personalizzato']}")
            print(f"Modifica totale: €{result['modifica_totale']}")
            print(f"Modifiche: {', '.join(result['modifiche'])}")
            return True
        else:
            print(f"Errore: {response.text}")
            return False
            
    except Exception as e:
        print(f"Errore: {e}")
        return False

def main():
    print("TEST MODIFICHE INGREDIENTI ORDINI")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Regole prezzo
    if test_price_rules():
        success_count += 1
    
    # Test 2: Endpoint ingredienti
    if test_ingredients_endpoint():
        success_count += 1
    
    # Test 3: Modifica ingredienti
    if test_modify_ingredients():
        success_count += 1
    
    print(f"\nRIEPILOGO: {success_count}/{total_tests} test superati")
    
    if success_count == total_tests:
        print("SUCCESSO: Tutti i test superati!")
        print("La funzionalità di modifica ingredienti è pronta")
    else:
        print("ATTENZIONE: Alcuni test falliti")
        print("Verifica i log per i dettagli")

if __name__ == "__main__":
    main()
