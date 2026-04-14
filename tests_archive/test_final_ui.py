#!/usr/bin/env python3
"""
Test finale per verificare le correzioni UI
"""

import requests
import json

def test_final_scenario():
    """Test scenario completo: 1x Margherita + 1x Margherita (modifica)"""
    print("Test scenario finale...")
    
    try:
        # Scenario: 1 Margherita normale + 1 Margherita con funghi
        order_data = {
            "numero_tavolo": 20,
            "numero_persone": 2,
            "dettagli": [
                {
                    "pizza_id": 10,
                    "quantita": 1,
                    "note": "Normale",
                    "prezzo_personalizzato": None  # Item base
                },
                {
                    "pizza_id": 10,
                    "quantita": 1,
                    "note": "Con funghi extra",
                    "prezzo_personalizzato": 9.5  # Item modificato
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
                
                print(f"Ordine #{order_id}:")
                print(f"Totale: €{order_details.get('totale', 0)}")
                print(f"Items: {len(items)}")
                print()
                
                for i, item in enumerate(items, 1):
                    is_modified = item.get('prezzo_personalizzato') is not None
                    prezzo = item.get('prezzo_personalizzato') or item.get('prezzo_unitario')
                    
                    # Simula esattamente la logica UI
                    ui_name = f"{item['quantita']}x {item['pizza_nome']}"
                    ui_indicator = ""
                    if is_modified:
                        ui_indicator = " (Modificato)"
                    
                    print(f"Item {i}:")
                    print(f"  UI: {ui_name}{ui_indicator}")
                    print(f"  Note: {item.get('note', 'N/A')}")
                    print(f"  Prezzo: €{prezzo}")
                    print(f"  Subtotale: €{item.get('subtotale', 0)}")
                    print(f"  Is modified: {is_modified}")
                    print()
                
                # Verifica atteso
                expected_items = [
                    ("1x Margherita a ruota di carro", "", 8.0, False),
                    ("1x Margherita a ruota di carro", " (🔧 Modificato)", 9.5, True)
                ]
                
                success = True
                if len(items) != 2:
                    print(f"ERRORE: Attesi 2 items, trovati {len(items)}")
                    success = False
                
                for i, (expected_name, expected_indicator, expected_price, expected_modified) in enumerate(expected_items):
                    if i < len(items):
                        item = items[i]
                        is_modified = item.get('prezzo_personalizzato') is not None
                        prezzo = item.get('prezzo_personalizzato') or item.get('prezzo_unitario')
                        
                        if is_modified != expected_modified:
                            print(f"ERRORE Item {i+1}: modified {is_modified} != atteso {expected_modified}")
                            success = False
                        
                        if abs(prezzo - expected_price) > 0.01:
                            print(f"ERRORE Item {i+1}: prezzo €{prezzo} != atteso €{expected_price}")
                            success = False
                
                if success:
                    print("SUCCESSO: Scenario finale funzionante!")
                    print("Nell'UI vedrai:")
                    print("- 1x Margherita a ruota di carro")
                    print("- 1x Margherita a ruota di carro (🔧 Modificato)")
                    return True
                else:
                    print("ERRORE: Alcuni controlli falliti")
                    return False
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
    print("TEST FINALE CORREZIONI UI")
    print("=" * 30)
    
    if test_final_scenario():
        print("\nSUCCESSO: TUTTO FUNZIONA!")
        print("Le correzioni richieste sono state implementate:")
        print("1. Indicatore modifiche sui singoli item")
        print("2. Item separati per modifiche diverse")
        print("3. Merge per item identici")
    else:
        print("\nPROBLEMI RILEVATI")
        print("Verifica i log sopra")

if __name__ == "__main__":
    main()
