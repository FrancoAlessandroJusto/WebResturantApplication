#!/usr/bin/env python3
"""
Test per verificare che i dati degli ordini includano numero_persone e coperto
"""

import requests
import json

def test_orders_data():
    """Verifica che i dati degli ordini contengano i campi corretti"""
    print("Test dati ordini...")
    
    try:
        # Test GET /orders (ordini attivi)
        response = requests.get("http://127.0.0.1:8000/orders")
        print(f"GET /orders status: {response.status_code}")
        
        if response.status_code == 200:
            orders = response.json()
            print(f"Ordini attivi trovati: {len(orders)}")
            
            if orders:
                # Analizza il primo ordine
                order = orders[0]
                print("\nPrimo ordine analizzato:")
                print(f"  ID: {order.get('id')}")
                print(f"  Tavolo: {order.get('numero_tavolo')}")
                print(f"  Numero persone: {order.get('numero_persone', 'NON PRESENTE')}")
                print(f"  Totale: €{order.get('totale', 0)}")
                print(f"  Coperto: €{order.get('coperto', 0)}")
                print(f"  Stato: {order.get('stato', 'NON PRESENTE')}")
                
                # Verifica campi essenziali
                issues = []
                if 'numero_persone' not in order:
                    issues.append("numero_persone mancante")
                if 'coperto' not in order:
                    issues.append("coperto mancante")
                if 'totale' not in order:
                    issues.append("totale mancante")
                
                if issues:
                    print(f"\nATTENZIONE: Campi mancanti: {', '.join(issues)}")
                else:
                    print("\nOK: Tutti i campi presenti")
                
                # Calcola expected totale
                articoli_total = sum(item.get('subtotale', 0) for item in order.get('dettagli', []))
                expected_total = articoli_total + (order.get('coperto', 0))
                actual_total = order.get('totale', 0)
                
                print(f"\nVerifica calcolo totale:")
                print(f"  Articoli: €{articoli_total:.2f}")
                print(f"  Coperto: €{order.get('coperto', 0):.2f}")
                print(f"  Atteso: €{expected_total:.2f}")
                print(f"  Effettivo: €{actual_total:.2f}")
                
                if abs(expected_total - actual_total) < 0.01:
                    print("  OK: Calcolo totale corretto")
                else:
                    print("  ERRORE: Calcolo totale errato!")
            else:
                print("Nessun ordine attivo da testare")
        else:
            print(f"Errore GET /orders: {response.text}")
        
        # Test GET /orders/{id} per dettagli
        if orders:
            order_id = orders[0]['id']
            print(f"\nTest GET /orders/{order_id}...")
            
            detail_response = requests.get(f"http://127.0.0.1:8000/orders/{order_id}")
            print(f"GET /orders/{order_id} status: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                order_detail = detail_response.json()
                print(f"  Numero persone: {order_detail.get('numero_persone', 'NON PRESENTE')}")
                print(f"  Coperto: €{order_detail.get('coperto', 0)}")
                print(f"  Dettagli: {len(order_detail.get('dettagli', []))} articoli")
            else:
                print(f"Errore dettagli ordine: {detail_response.text}")
        
    except Exception as e:
        print(f"Errore durante il test: {e}")

if __name__ == "__main__":
    print("TEST DATI ORDINI")
    print("=" * 40)
    test_orders_data()
