#!/usr/bin/env python3
"""
Test per verificare che il calcolo del totale ordine funzioni correttamente con prezzi personalizzati
"""

import requests
import json

def test_order_total_with_customized_prices():
    """Test creazione ordine con prezzi personalizzati"""
    print("Test calcolo totale con prezzi personalizzati...")
    
    try:
        # Dati di test con prezzi personalizzati
        order_data = {
            "numero_tavolo": 5,  # Tavolo valido per evitare conflitti
            "numero_persone": 2,
            "dettagli": [
                {
                    "pizza_id": 10,  # Pizza Margherita (base €8.0)
                    "quantita": 2,
                    "note": "Senza cipolla",
                    "prezzo_personalizzato": 9.5  # +€1.5 per formaggio extra
                },
                {
                    "pizza_id": 11,  # Pizza Diavola (base €10.0)
                    "quantita": 1,
                    "note": "Extra piccante",
                    "prezzo_personalizzato": 12.0  # +€2.0 per carne extra
                }
            ]
        }
        
        # Calcolo atteso: (9.5 × 2) + (12.0 × 1) + coperto (2×2€) = 19.0 + 12.0 + 4.0 = €35.0
        expected_total = 35.0
        
        print(f"Dati ordine: {json.dumps(order_data, indent=2)}")
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
            for dettaglio in result.get('dettagli', []):
                print(f"    - {dettaglio['pizza_nome']}: €{dettaglio.get('prezzo_personalizzato', dettaglio['prezzo_unitario'])} × {dettaglio['quantita']} = €{dettaglio['subtotale']}")
            
            # Verifica totale
            if abs(actual_total - expected_total) < 0.01:
                print(f"SUCCESSO: Calcolo totale corretto!")
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

def test_order_total_without_customization():
    """Test creazione ordine senza prezzi personalizzati (controllo)"""
    print("\nTest calcolo totale senza personalizzazioni...")
    
    try:
        # Dati di test senza prezzi personalizzati
        order_data = {
            "numero_tavolo": 2,
            "numero_persone": 1,
            "dettagli": [
                {
                    "pizza_id": 10,  # Pizza Margherita (base €8.0)
                    "quantita": 1,
                    "note": "Normale"
                    # Nessun prezzo_personalizzato
                }
            ]
        }
        
        # Calcolo atteso: (8.0 × 1) + coperto (1×2€) = 8.0 + 2.0 = €10.0
        expected_total = 10.0
        
        response = requests.post("http://127.0.0.1:8000/orders", json=order_data)
        print(f"POST /orders status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            actual_total = result.get("totale", 0)
            
            print(f"Totale: €{actual_total} (atteso: €{expected_total})")
            
            if abs(actual_total - expected_total) < 0.01:
                print(f"SUCCESSO: Calcolo totale senza personalizzazioni corretto!")
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
    print("TEST CALCOLO TOTALE ORDINI CON PREZZI PERSONALIZZATI")
    print("=" * 60)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Con prezzi personalizzati
    if test_order_total_with_customized_prices():
        success_count += 1
    
    # Test 2: Senza prezzi personalizzati
    if test_order_total_without_customization():
        success_count += 1
    
    print(f"\nRIEPILOGO: {success_count}/{total_tests} test superati")
    
    if success_count == total_tests:
        print("SUCCESSO: Calcolo totale ordini funzionante correttamente!")
        print("Prezzi personalizzati calcolati correttamente")
        print("Prezzi base funzionanti come controllo")
    else:
        print("ATTENZIONE: Problemi nel calcolo del totale")
        print("Verifica i log per i dettagli")

if __name__ == "__main__":
    main()
