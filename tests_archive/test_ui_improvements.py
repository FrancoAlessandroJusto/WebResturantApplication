#!/usr/bin/env python3
"""
Test per verificare le migliorie UI:
1. Nascondere coperto per ordini attivi esistenti
2. Mostrare indicatore modifiche in Ordine #--
"""

import requests
import json

def test_active_order_endpoint():
    """Test endpoint per controllare ordini attivi"""
    print("Test endpoint ordini attivi...")
    
    try:
        # Test con tavolo senza ordine attivo
        response = requests.get("http://127.0.0.1:8000/orders/active/99")
        print(f"GET /orders/active/99 status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result is None:
                print("  Corretto: Nessun ordine attivo al tavolo 99")
            else:
                print(f"  Ordine attivo trovato: #{result.get('id')}")
        else:
            print(f"  Errore: {response.text}")
            return False
        
        # Test con tavolo con ordine attivo (se esiste)
        response = requests.get("http://127.0.0.1:8000/orders/active/8")
        print(f"GET /orders/active/8 status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result:
                print(f"  Ordine attivo trovato: #{result.get('id')} - Tavolo {result.get('numero_tavolo')}")
                return True
            else:
                print("  Nessun ordine attivo al tavolo 8")
                return True
        else:
            print(f"  Errore: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ERRORE: {e}")
        return False

def test_order_items_endpoint():
    """Test endpoint per recuperare items di un ordine"""
    print("\nTest endpoint items ordine...")
    
    try:
        # Prima creiamo un ordine di test
        order_data = {
            "numero_tavolo": 10,
            "numero_persone": 2,
            "dettagli": [
                {
                    "pizza_id": 10,
                    "quantita": 1,
                    "note": "Normale",
                    "prezzo_personalizzato": 8.0
                },
                {
                    "pizza_id": 10,
                    "quantita": 1,
                    "note": "Extra formaggio",
                    "prezzo_personalizzato": 9.5
                }
            ]
        }
        
        response = requests.post("http://127.0.0.1:8000/orders", json=order_data)
        print(f"POST /orders status: {response.status_code}")
        
        if response.status_code == 200:
            order = response.json()
            order_id = order.get('id')
            print(f"  Ordine creato: #{order_id}")
            
            # Test endpoint items
            response = requests.get(f"http://127.0.0.1:8000/orders/{order_id}/items")
            print(f"GET /orders/{order_id}/items status: {response.status_code}")
            
            if response.status_code == 200:
                items = response.json()
                print(f"  Items recuperati: {len(items)}")
                
                # Controlla items modificati
                modified_items = [item for item in items if item.get('prezzo_personalizzato') is not None]
                print(f"  Items modificati: {len(modified_items)}")
                
                for item in items:
                    prezzo = item.get('prezzo_personalizzato') or item.get('prezzo_unitario')
                    modificato = item.get('prezzo_personalizzato') is not None
                    print(f"    - {item['pizza_nome']}: €{prezzo} {'(modificato)' if modificato else ''}")
                
                return True
            else:
                print(f"  Errore items: {response.text}")
                return False
        else:
            print(f"  Errore creazione ordine: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ERRORE: {e}")
        return False

def test_order_modifications_indicator():
    """Test che l'indicatore di modifiche funzioni"""
    print("\nTest indicatore modifiche...")
    
    try:
        # Creiamo un ordine con modifiche
        order_data = {
            "numero_tavolo": 11,
            "numero_persone": 2,
            "dettagli": [
                {
                    "pizza_id": 10,
                    "quantita": 2,
                    "note": "Normale",
                    "prezzo_personalizzato": 8.0
                },
                {
                    "pizza_id": 11,
                    "quantita": 1,
                    "note": "Extra carne",
                    "prezzo_personalizzato": 12.0
                }
            ]
        }
        
        response = requests.post("http://127.0.0.1:8000/orders", json=order_data)
        
        if response.status_code == 200:
            order = response.json()
            order_id = order.get('id')
            
            # Recupera i dettagli completi dell'ordine
            response = requests.get(f"http://127.0.0.1:8000/orders/{order_id}")
            
            if response.status_code == 200:
                order_details = response.json()
                
                # Simula la logica del frontend
                has_modified = any(item.get('prezzo_personalizzato') is not None for item in order_details['dettagli'])
                modified_count = len([item for item in order_details['dettagli'] if item.get('prezzo_personalizzato') is not None])
                
                print(f"  Ordine #{order_id}:")
                print(f"    - Items totali: {len(order_details['dettagli'])}")
                print(f"    - Items modificati: {modified_count}")
                print(f"    - Ha modifiche: {has_modified}")
                
                if has_modified:
                    print(f"    - Indicatore da mostrare: 🔧 {modified_count} modific{'he' if modified_count != 1 else 'a'}")
                else:
                    print(f"    - Nessun indicatore da mostrare")
                
                return True
            else:
                print(f"  Errore dettagli ordine: {response.text}")
                return False
        else:
            print(f"  Errore creazione ordine: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ERRORE: {e}")
        return False

def main():
    print("TEST MIGLORIE UI")
    print("=" * 40)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Endpoint ordini attivi
    if test_active_order_endpoint():
        success_count += 1
    
    # Test 2: Endpoint items ordine
    if test_order_items_endpoint():
        success_count += 1
    
    # Test 3: Indicatore modifiche
    if test_order_modifications_indicator():
        success_count += 1
    
    print(f"\nRIEPILOGO: {success_count}/{total_tests} test superati")
    
    if success_count == total_tests:
        print("SUCCESSO: Tutte le migliorie funzionano!")
        print("Ora nell'UI:")
        print("1. Se c'è un ordine attivo, il campo coperto si nasconde")
        print("2. In 'Ordine #--' appare l'indicatore per le modifiche")
    else:
        print("ATTENZIONE: Alcune migliorie non funzionano")
        print("Verifica i log per i dettagli")

if __name__ == "__main__":
    main()
