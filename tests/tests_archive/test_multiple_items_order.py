#!/usr/bin/env python3
"""
Test per verificare che più item dello stesso tipo possano coesistere con modifiche diverse
"""

import requests
import json

def test_multiple_items_same_pizza():
    """Test creazione ordine con 2 Margherita, una normale e una modificata"""
    print("Test ordine con 2 Margherita (normale + modificata)...")
    
    try:
        # Dati di test: 2 Margherita, una normale e una con extra formaggio
        order_data = {
            "numero_tavolo": 8,  # Tavolo diverso per evitare conflitti
            "numero_persone": 2,
            "dettagli": [
                {
                    "pizza_id": 10,  # Margherita base
                    "quantita": 1,
                    "note": "Normale",
                    "prezzo_personalizzato": 8.0,  # Prezzo base
                },
                {
                    "pizza_id": 10,  # Stessa Margherita ma modificata
                    "quantita": 1,
                    "note": "Extra formaggio",
                    "prezzo_personalizzato": 9.5,  # +€1.5 per formaggio extra
                    "modifiche": ["+formaggio_extra"]
                }
            ]
        }
        
        # Calcolo atteso: (8.0 × 1) + (9.5 × 1) + coperto (2×2€) = 8.0 + 9.5 + 4.0 = €21.5
        expected_total = 21.5
        
        print(f"Dati ordine:")
        for i, dettaglio in enumerate(order_data["dettagli"], 1):
            print(f"  {i}. Pizza {dettaglio['pizza_id']}: €{dettaglio['prezzo_personalizzato']} × {dettaglio['quantita']} = €{dettaglio['prezzo_personalizzato'] * dettaglio['quantita']}")
            print(f"     Note: {dettaglio['note']}")
            if dettaglio.get('modifiche'):
                print(f"     Modifiche: {', '.join(dettaglio['modifiche'])}")
        
        print(f"Totale atteso: €{expected_total}")
        
        response = requests.post("http://127.0.0.1:8000/orders", json=order_data)
        print(f"POST /orders status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            actual_total = result.get("totale", 0)
            
            print(f"Risultato:")
            print(f"  ID Ordine: {result.get('id')}")
            print(f"  Tavolo: {result.get('numero_tavolo')}")
            print(f"  Totale: €{actual_total}")
            print(f"  Dettagli: {len(result.get('dettagli', []))}")
            
            # Verifica dettagli
            for i, dettaglio in enumerate(result.get('dettagli', []), 1):
                prezzo_usato = dettaglio.get('prezzo_personalizzato') or dettaglio['prezzo_unitario']
                print(f"    {i}. {dettaglio['pizza_nome']}: €{prezzo_usato} × {dettaglio['quantita']} = €{dettaglio['subtotale']}")
                if dettaglio.get('note'):
                    print(f"       Note: {dettaglio['note']}")
            
            # Verifica totale
            if abs(actual_total - expected_total) < 0.01:
                print(f"SUCCESSO: Calcolo totale corretto!")
                print(f"Le 2 Margherita con prezzi diversi sono state gestite correttamente")
                return True
            else:
                print(f"ERRORE: Totale calcolato €{actual_total} != atteso €{expected_total}")
                return False
        else:
            print(f"ERRORE: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def test_different_pizzas_with_modifications():
    """Test con pizze diverse e modifiche miste"""
    print("\nTest pizze diverse con modifiche miste...")
    
    try:
        order_data = {
            "numero_tavolo": 9,
            "numero_persone": 3,
            "dettagli": [
                {
                    "pizza_id": 10,  # Margherita
                    "quantita": 2,
                    "note": "Normale",
                    "prezzo_personalizzato": 8.0
                },
                {
                    "pizza_id": 11,  # Diavola
                    "quantita": 1,
                    "note": "Extra piccante",
                    "prezzo_personalizzato": 12.0,
                    "modifiche": ["+carne_extra"]
                },
                {
                    "pizza_id": 10,  # Altra Margherita modificata
                    "quantita": 1,
                    "note": "Senza formaggio",
                    "prezzo_personalizzato": 7.5,  # -€0.5 per rimozione
                    "modifiche": ["-formaggio"]
                }
            ]
        }
        
        # Calcolo atteso: (8.0 × 2) + (12.0 × 1) + (7.5 × 1) + coperto (3×2€) = 16.0 + 12.0 + 7.5 + 6.0 = €41.5
        expected_total = 41.5
        
        response = requests.post("http://127.0.0.1:8000/orders", json=order_data)
        
        if response.status_code == 200:
            result = response.json()
            actual_total = result.get("totale", 0)
            
            print(f"Totale: €{actual_total} (atteso: €{expected_total})")
            
            if abs(actual_total - expected_total) < 0.01:
                print(f"SUCCESSO: Gestione modifiche miste corretta!")
                return True
            else:
                print(f"ERRORE: Totale calcolato €{actual_total} != atteso €{expected_total}")
                return False
        else:
            print(f"ERRORE: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def main():
    print("TEST GESTIONE MULTIPLI ITEM STESSO ORDINE")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Stessa pizza con modifiche diverse
    if test_multiple_items_same_pizza():
        success_count += 1
    
    # Test 2: Pizze diverse con modifiche miste
    if test_different_pizzas_with_modifications():
        success_count += 1
    
    print(f"\nRIEPILOGO: {success_count}/{total_tests} test superati")
    
    if success_count == total_tests:
        print("SUCCESSO: Gestione multipli item funzionante!")
        print("Ora puoi avere:")
        print("- 2 Margherita, una normale e una modificata")
        print("- Stessa pizza con prezzi diversi")
        print("- Modifiche indipendenti per ogni item")
    else:
        print("ATTENZIONE: Problemi nella gestione multi-item")
        print("Verifica i log per i dettagli")

if __name__ == "__main__":
    main()
