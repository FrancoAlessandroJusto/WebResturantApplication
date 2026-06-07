#!/usr/bin/env python3
"""
Test per verificare che il frontend carichi correttamente gli ingredienti per nuovi ordini
"""

import requests
import json

def test_menu_endpoint():
    """Test che l'endpoint /menu/{id} funzioni correttamente"""
    print("Test endpoint menu per ingredienti...")
    
    try:
        # Test con un pizza_id esistente
        pizza_id = 10
        response = requests.get(f"http://127.0.0.1:8000/menu/{pizza_id}")
        print(f"GET /menu/{pizza_id} status: {response.status_code}")
        
        if response.status_code == 200:
            menu_item = response.json()
            print(f"  Nome: {menu_item.get('nome', 'N/A')}")
            print(f"  Prezzo: €{menu_item.get('prezzo', 0)}")
            print(f"  Ingredienti: {len(menu_item.get('ingredienti', []))}")
            
            # Verifica struttura ingredienti
            ingredienti = menu_item.get('ingredienti', [])
            if ingredienti:
                primo_ingrediente = ingredienti[0]
                print(f"  Primo ingrediente: {primo_ingrediente.get('nome', 'N/A')} ({primo_ingrediente.get('tipo', 'N/A')})")
            
            return True
        else:
            print(f"Errore: {response.text}")
            return False
            
    except Exception as e:
        print(f"Errore: {e}")
        return False

def test_ingredients_endpoint():
    """Test che l'endpoint ingredienti funzioni correttamente"""
    print("\nTest endpoint ingredienti disponibili...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/ingredienti")
        print(f"GET /ingredienti status: {response.status_code}")
        
        if response.status_code == 200:
            ingredienti = response.json()
            print(f"  Ingredienti disponibili: {len(ingredienti)}")
            
            if ingredienti:
                # Verifica struttura
                primo = ingredienti[0]
                print(f"  Primo: {primo.get('nome', 'N/A')} ({primo.get('tipo', 'N/A')}) - ID: {primo.get('id', 'N/A')}")
            
            return True
        else:
            print(f"Errore: {response.text}")
            return False
            
    except Exception as e:
        print(f"Errore: {e}")
        return False

def test_new_order_ingredients_flow():
    """Test del flusso completo per nuovo ordine"""
    print("\nTest flusso ingredienti per nuovo ordine...")
    
    try:
        # 1. Carica menu item (simula frontend)
        pizza_id = 10
        menu_response = requests.get(f"http://127.0.0.1:8000/menu/{pizza_id}")
        
        if menu_response.status_code != 200:
            print(f"ERRORE: Menu non caricabile")
            return False
        
        menu_item = menu_response.json()
        base_ingredients = menu_item.get('ingredienti', [])
        print(f"  1. Menu caricato: {menu_item.get('nome')} con {len(base_ingredients)} ingredienti base")
        
        # 2. Carica ingredienti disponibili (simula frontend)
        ingredients_response = requests.get("http://127.0.0.1:8000/ingredienti")
        
        if ingredients_response.status_code != 200:
            print(f"ERRORE: Ingredienti non caricabili")
            return False
        
        all_ingredients = ingredients_response.json()
        print(f"  2. Ingredienti disponibili: {len(all_ingredients)}")
        
        # 3. Simula separazione ingredienti base/disponibili
        base_names = {ing['nome'] for ing in base_ingredients}
        available = [ing for ing in all_ingredients if ing['nome'] not in base_names]
        
        print(f"  3. Separazione completata:")
        print(f"     - Ingredienti base: {len(base_ingredients)}")
        print(f"     - Ingredienti aggiuntivi: {len(available)}")
        
        # 4. Simula calcolo prezzo con modifiche
        base_price = menu_item.get('prezzo', 0)
        price_change = 1.5  # Aggiunta formaggio
        
        new_price = base_price + price_change
        print(f"  4. Calcolo prezzo:")
        print(f"     - Prezzo base: €{base_price}")
        print(f"     - Modifica: +€{price_change}")
        print(f"     - Nuovo prezzo: €{new_price}")
        
        return True
        
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def main():
    print("TEST FRONTEND INGREDIENTI PER NUOVI ORDINI")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Endpoint menu
    if test_menu_endpoint():
        success_count += 1
    
    # Test 2: Endpoint ingredienti
    if test_ingredients_endpoint():
        success_count += 1
    
    # Test 3: Flusso completo
    if test_new_order_ingredients_flow():
        success_count += 1
    
    print(f"\nRIEPILOGO: {success_count}/{total_tests} test superati")
    
    if success_count == total_tests:
        print("SUCCESSO: Frontend ingredienti funzionante!")
        print("Il problema 404 dovrebbe essere risolto")
    else:
        print("ATTENZIONE: Problemi riscontrati")
        print("Verifica i log per i dettagli")

if __name__ == "__main__":
    main()
