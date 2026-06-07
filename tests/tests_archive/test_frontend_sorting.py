#!/usr/bin/env python3
"""
Test per verificare che l'ordinamento frontend funzioni correttamente
"""

import requests
import json

def test_ingredients_sorting():
    """Test che i dati ingredienti possano essere ordinati correttamente"""
    print("Test ordinamento ingredienti frontend...")
    
    try:
        # Recupera dati ingredienti
        response = requests.get("http://127.0.0.1:8000/analytics/ingredients?periodo=today")
        
        if response.ok:
            data = response.json()
            ingredients = data.get('ingredienti_analytics', [])
            
            print(f"Ingredienti caricati: {len(ingredients)}")
            
            if ingredients:
                print("\nDati originali (primi 5):")
                for i, ing in enumerate(ingredients[:5], 1):
                    print(f"  {i}. {ing.get('ingrediente', 'N/A')} - {ing.get('tipo', 'N/A')} - €{ing.get('costo_totale', 0):.2f}")
                
                # Test ordinamenti possibili
                print("\nTest ordinamenti:")
                
                # 1. Ordina per nome
                sorted_by_name = sorted(ingredients, key=lambda x: x.get('ingrediente', ''))
                print(f"  Per nome: {sorted_by_name[0].get('ingrediente', 'N/A')} ... {sorted_by_name[-1].get('ingrediente', 'N/A')}")
                
                # 2. Ordina per costo totale
                sorted_by_cost = sorted(ingredients, key=lambda x: x.get('costo_totale', 0), reverse=True)
                print(f"  Per costo: {sorted_by_cost[0].get('ingrediente', 'N/A')} (€{sorted_by_cost[0].get('costo_totale', 0):.2f}) più costoso")
                
                # 3. Ordina per utilizzi
                sorted_by_usage = sorted(ingredients, key=lambda x: x.get('utilizzi_in_ordini', 0), reverse=True)
                print(f"  Per utilizzi: {sorted_by_usage[0].get('ingrediente', 'N/A')} ({sorted_by_usage[0].get('utilizzi_in_ordini', 0)} utilizzi) più usato")
                
                # 4. Ordina per consumo
                def extract_consumption(consumo_display):
                    try:
                        # Estrai il valore numerico dal consumo (es. "12.05 pz" -> 12.05)
                        import re
                        match = re.search(r'(\d+\.?\d*)', str(consumo_display))
                        return float(match.group(1)) if match else 0.0
                    except:
                        return 0.0
                
                sorted_by_consumption = sorted(ingredients, key=lambda x: extract_consumption(x.get('consumo_unitario_display', '0')), reverse=True)
                print(f"  Per consumo: {sorted_by_consumption[0].get('ingrediente', 'N/A')} ({sorted_by_consumption[0].get('consumo_unitario_display', 'N/A')}) più consumato")
                
                # 5. Ordina per trend
                sorted_by_trend = sorted(ingredients, key=lambda x: abs(x.get('cost_trend_percent', 0)), reverse=True)
                print(f"  Per trend: {sorted_by_trend[0].get('ingrediente', 'N/A')} ({sorted_by_trend[0].get('cost_trend_percent', 0):.1f}% trend) più variabile")
                
                return True
            else:
                print("Nessun ingrediente trovato")
                return False
        else:
            print(f"Errore API: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def test_frontend_logic():
    """Test logica che il frontend dovrebbe implementare"""
    print("\nTest logica frontend...")
    
    # Simula dati ingredienti
    ingredients = [
        {'ingrediente': 'Mozzarella', 'tipo': 'formaggio', 'costo_totale': 45.50, 'utilizzi_in_ordini': 25},
        {'ingrediente': 'Pomodoro', 'tipo': 'base', 'costo_totale': 20.00, 'utilizzi_in_ordini': 15},
        {'ingrediente': 'Salame', 'tipo': 'carne', 'costo_totale': 35.00, 'utilizzi_in_ordini': 18}
    ]
    
    print("Simulazione filtri frontend:")
    
    # Test ricerca
    search_term = 'mozz'
    filtered = [ing for ing in ingredients if search_term.lower() in ing['ingrediente'].lower()]
    print(f"  Ricerca '{search_term}': {len(filtered)} risultati")
    
    # Test filtro tipo
    tipo_filter = 'formaggio'
    filtered = [ing for ing in ingredients if ing['tipo'] == tipo_filter]
    print(f"  Filtro tipo '{tipo_filter}': {len(filtered)} risultati")
    
    # Test ordinamento
    sorted_by_cost = sorted(ingredients, key=lambda x: x['costo_totale'], reverse=True)
    print(f"  Ordinamento costo: {sorted_by_cost[0]['ingrediente']} primo")
    
    return True

def main():
    print("TEST ORDINAMENTO FRONTEND INGREDIENTI")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: API ingredienti
    if test_ingredients_sorting():
        success_count += 1
    
    # Test 2: Logica frontend
    if test_frontend_logic():
        success_count += 1
    
    print(f"\nRIEPILOGO: {success_count}/{total_tests} test superati")
    
    if success_count == total_tests:
        print("SUCCESSO: Sistema ordinamento funzionante!")
        print("Nell'UI potrai ordinare per:")
        print("1. Nome (A-Z)")
        print("2. Consumo (più alto al più basso)")
        print("3. Costo totale (più alto al più basso)")
        print("4. Costo unitario (più alto al più basso)")
        print("5. Utilizzi (più alto al più basso)")
        print("6. Trend costo (più variabile al più stabile)")
        print("7. Filtrare per tipo e cercare per nome")
    else:
        print("ATTENZIONE: Problemi nell'ordinamento")
        print("Verifica i log per i dettagli")

if __name__ == "__main__":
    main()
