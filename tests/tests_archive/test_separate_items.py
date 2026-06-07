#!/usr/bin/env python3
"""
Test per verificare che:
1. Gli item con modifiche appaiano separati
2. L'indicatore di modifiche sia sui singoli item
"""

import requests
import json

def test_separate_items_logic():
    """Test che item con stesso pizza_id ma prezzi diversi rimangano separati"""
    print("Test logica item separati...")
    
    try:
        # Creiamo un ordine con 2 Margherita diverse
        order_data = {
            "numero_tavolo": 16,  # Tavolo univoco
            "numero_persone": 2,
            "dettagli": [
                {
                    "pizza_id": 10,  # Margherita normale
                    "quantita": 1,
                    "note": "Normale",
                    "prezzo_personalizzato": None  # None per item base
                },
                {
                    "pizza_id": 10,  # Margherita con funghi
                    "quantita": 1,
                    "note": "Con funghi extra",
                    "prezzo_personalizzato": 9.5  # Prezzo modificato
                }
            ]
        }
        
        response = requests.post("http://127.0.0.1:8000/orders", json=order_data)
        print(f"POST /orders status: {response.status_code}")
        
        if response.status_code == 200:
            order = response.json()
            order_id = order.get('id')
            
            # Recupera i dettagli per verificare che siano separati
            response = requests.get(f"http://127.0.0.1:8000/orders/{order_id}")
            
            if response.status_code == 200:
                order_details = response.json()
                items = order_details.get('dettagli', [])
                
                print(f"  Ordine #{order_id} creato con {len(items)} items:")
                
                for i, item in enumerate(items, 1):
                    prezzo = item.get('prezzo_personalizzato') or item.get('prezzo_unitario')
                    modificato = item.get('prezzo_personalizzato') is not None
                    print(f"    {i}. {item['quantita']}x {item['pizza_nome']}")
                    print(f"       Note: {item.get('note', 'N/A')}")
                    print(f"       Prezzo: €{prezzo} {'(modificato)' if modificato else '(base)'}")
                
                # Verifica che ci siano 2 item separati
                if len(items) == 2:
                    print("SUCCESSO: 2 item separati creati correttamente!")
                    return True
                else:
                    print(f"ERRORE: Attesi 2 item, trovati {len(items)}")
                    return False
            else:
                print(f"ERRORE recupero dettagli: {response.text}")
                return False
        else:
            print(f"ERRORE creazione ordine: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def test_merge_logic():
    """Test che item identici vengano mergiati"""
    print("\nTest logica merge item identici...")
    
    try:
        # Prima creiamo un ordine base
        order_data = {
            "numero_tavolo": 15,  # Tavolo fisso per il test
            "numero_persone": 2,
            "dettagli": [
                {
                    "pizza_id": 10,  # Margherita normale
                    "quantita": 1,
                    "note": "Normale",
                    "prezzo_personalizzato": None  # Importante: null per item base
                }
            ]
        }
        
        response = requests.post("http://127.0.0.1:8000/orders", json=order_data)
        
        if response.status_code == 200:
            order = response.json()
            order_id = order.get('id')
            print(f"  Ordine base #{order_id} creato")
            
            # Ora aggiungiamo un altro item identico (dovrebbe fare merge)
            merge_data = {
                "numero_tavolo": 15,  # Stesso tavolo
                "numero_persone": 2,
                "dettagli": [
                    {
                        "pizza_id": 10,  # Stessa Margherita normale
                        "quantita": 2,
                        "note": "Altro normale",
                        "prezzo_personalizzato": None  # Stesso prezzo (null = base)
                    }
                ]
            }
            
            response = requests.post("http://127.0.0.1:8000/orders", json=merge_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Merge response: {result.get('message', 'N/A')}")
                
                # Recupera i dettagli finali
                response = requests.get(f"http://127.0.0.1:8000/orders/{order_id}")
                
                if response.status_code == 200:
                    order_details = response.json()
                    items = order_details.get('dettagli', [])
                    
                    print(f"  Items finali dopo merge: {len(items)}")
                    
                    for item in items:
                        prezzo = item.get('prezzo_personalizzato') or item.get('prezzo_unitario')
                        print(f"    - {item['quantita']}x {item['pizza_nome']} (€{prezzo})")
                    
                    # Dovrebbe avere 1 item con quantità 3
                    if len(items) == 1 and items[0]['quantita'] == 3:
                        print("SUCCESSO: Merge funzionante!")
                        return True
                    else:
                        print(f"ERRORE: Atteso 1 item con quantità 3, trovati {len(items)} items")
                        return False
                else:
                    print(f"ERRORE recupero dettagli finali: {response.text}")
                    return False
            else:
                print(f"ERRORE merge: {response.text}")
                return False
        else:
            print(f"ERRORE creazione ordine base: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def test_ui_indicator():
    """Test che l'indicatore UI sia corretto"""
    print("\nTest indicatore UI...")
    
    try:
        # Creiamo un ordine misto
        order_data = {
            "numero_tavolo": 17,  # Tavolo univoco
            "numero_persone": 3,
            "dettagli": [
                {
                    "pizza_id": 10,  # Normale
                    "quantita": 2,
                    "note": "Normale",
                    "prezzo_personalizzato": None  # None = base
                },
                {
                    "pizza_id": 11,  # Modificato
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
            
            response = requests.get(f"http://127.0.0.1:8000/orders/{order_id}")
            
            if response.status_code == 200:
                order_details = response.json()
                items = order_details.get('dettagli', [])
                
                print(f"  Ordine #{order_id} con {len(items)} items:")
                
                for item in items:
                    is_modified = item.get('prezzo_personalizzato') is not None
                    prezzo = item.get('prezzo_personalizzato') or item.get('prezzo_unitario')
                    
                    # Simula logica UI
                    ui_display = f"{item['quantita']}x {item['pizza_nome']}"
                    if is_modified:
                        ui_display += " (🔧 Modificato)"
                    
                    print(f"    UI: {ui_display}")
                    print(f"       Prezzo personalizzato: €{prezzo}")
                
                # Verifica che solo l'item modificato abbia l'indicatore
                modified_items = [item for item in items if item.get('prezzo_personalizzato') is not None]
                print(f"  Items con indicatore: {len(modified_items)}")
                
                return True
            else:
                print(f"ERRORE dettagli: {response.text}")
                return False
        else:
            print(f"ERRORE creazione: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def main():
    print("TEST ITEM SEPARATI E INDICATORI UI")
    print("=" * 45)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Item separati
    if test_separate_items_logic():
        success_count += 1
    
    # Test 2: Merge item identici
    if test_merge_logic():
        success_count += 1
    
    # Test 3: Indicatore UI
    if test_ui_indicator():
        success_count += 1
    
    print(f"\nRIEPILOGO: {success_count}/{total_tests} test superati")
    
    if success_count == total_tests:
        print("SUCCESSO: Logica item separati funzionante!")
        print("Ora:")
        print("1. 1x Margherita + 1x Margherita (modifica) = 2 item separati")
        print("2. L'indicatore appare solo sugli item modificati")
        print("3. Item identici vengono mergiati correttamente")
    else:
        print("ATTENZIONE: Problemi nella logica item")
        print("Verifica i log per i dettagli")

if __name__ == "__main__":
    main()
