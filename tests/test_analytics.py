#!/usr/bin/env python3
import sys
import requests

def test_analytics_api():
    try:
        # Test API analytics
        response = requests.get("http://127.0.0.1:8000/analytics/summary?periodo=today")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("Response data:")
            print(f"  Periodo: {data.get('periodo', 'N/A')}")
            print(f"  Ricavo: €{data.get('ricavo_totale', 0):.2f}")
            print(f"  Costo: €{data.get('costo_produzione_totale', 0):.2f}")
            print(f"  Profitto: €{data.get('profitto_netto', 0):.2f}")
            print(f"  Ordini: {data.get('numero_ordini', 0)}")
            print(f"  Items: {len(data.get('items_analytics', []))}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_analytics_api()
