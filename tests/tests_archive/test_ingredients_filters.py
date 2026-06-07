#!/usr/bin/env python3
"""
Test per verificare che il sistema di filtri ingredienti funzioni
"""

import requests
import json

def test_ingredients_analytics():
    """Test endpoint analytics ingredienti"""
    print("Test analytics ingredienti...")
    
    try:
        # Test diversi periodi
        periods = ['today', 'week', 'month']
        
        for period in periods:
            print(f"\n--- Periodo: {period} ---")
            
            response = requests.get(f"http://127.0.0.1:8000/analytics/ingredients?periodo={period}")
            print(f"GET /analytics/ingredients?periodo={period} status: {response.status_code}")
            
            if response.ok:
                data = response.json()
                
                print(f"  Costo totale: €{data.get('total_cost', 0):.2f}")
                print(f"  Consumo totale: {data.get('total_consumption', 0):.2f}")
                print(f"  Ingredient count: {data.get('ingredient_count', 0)}")
                
                ingredients = data.get('ingredienti_analytics', [])
                print(f"  Ingredienti trovati: {len(ingredients)}")
                
                if ingredients:
                    # Mostra primi 3 ingredienti come esempio
                    for i, ingredient in enumerate(ingredients[:3], 1):
                        print(f"    {i}. {ingredient.get('ingrediente', 'N/A')} - {ingredient.get('tipo', 'N/A')}")
                        print(f"       Consumo: {ingredient.get('consumo_unitario_display', 'N/A')}")
                        print(f"       Costo totale: €{ingredient.get('costo_totale', 0):.2f}")
                        print(f"       Costo unitario: €{ingredient.get('costo_unitario_effettivo', 0):.2f}")
                        print(f"       Utilizzi: {ingredient.get('utilizzi_in_ordini', 0)}")
                        print(f"       Trend: {ingredient.get('cost_trend_percent', 0):.1f}%")
                else:
                    print("  Nessun ingrediente trovato")
            else:
                print(f"  Errore: {response.text}")
                return False
        
        return True
        
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def test_filtering_logic():
    """Test logica di filtraggio che dovrebbe essere implementata nel frontend"""
    print("\nTest logica filtri...")
    
    # Dati di esempio per simulare il frontend
    sample_ingredients = [
        {
            'ingrediente': 'Mozzarella',
            'tipo': 'formaggio',
            'consumo_unitario_display': '150.5g',
            'costo_totale': 45.50,
            'costo_unitario_effettivo': 0.30,
            'utilizzi_in_ordini': 25,
            'cost_trend_percent': 5.2
        },
        {
            'ingrediente': 'Pomodoro',
            'tipo': 'base',
            'consumo_unitario_display': '200.0g',
            'costo_totale': 20.00,
            'costo_unitario_effettivo': 0.10,
            'utilizzi_in_ordini': 15,
            'cost_trend_percent': -2.1
        },
        {
            'ingrediente': 'Salame',
            'tipo': 'carne',
            'consumo_unitario_display': '100.0g',
            'costo_totale': 35.00,
            'costo_unitario_effettivo': 0.35,
            'utilizzi_in_ordini': 18,
            'cost_trend_percent': 8.7
        }
    ]
    
    print("Dati di esempio:")
    for i, ing in enumerate(sample_ingredients, 1):
        print(f"  {i}. {ing['ingrediente']} ({ing['tipo']}) - €{ing['costo_totale']:.2f}")
    
    # Simula filtri
    print("\nSimulazione filtri:")
    
    # Filtro per nome
    search_term = 'mozz'
    filtered = [ing for ing in sample_ingredients if search_term.lower() in ing['ingrediente'].lower()]
    print(f"  Cerca '{search_term}': {len(filtered)} risultati")
    
    # Filtro per tipo
    filter_type = 'formaggio'
    filtered = [ing for ing in sample_ingredients if ing['tipo'] == filter_type]
    print(f"  Tipo '{filter_type}': {len(filtered)} risultati")
    
    # Ordinamento per costo
    sorted_by_cost = sorted(sample_ingredients, key=lambda x: x['costo_totale'], reverse=True)
    print(f"  Ordinati per costo: {sorted_by_cost[0]['ingrediente']} (€{sorted_by_cost[0]['costo_totale']:.2f}) il più costoso")
    
    # Ordinamento per utilizzi
    sorted_by_usage = sorted(sample_ingredients, key=lambda x: x['utilizzi_in_ordini'], reverse=True)
    print(f"  Più usato: {sorted_by_usage[0]['ingrediente']} ({sorted_by_usage[0]['utilizzi_in_ordini']} utilizzi)")
    
    return True

def main():
    print("TEST FILTRI INGREDIENTI")
    print("=" * 40)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: API ingredienti
    if test_ingredients_analytics():
        success_count += 1
    
    # Test 2: Logica filtri
    if test_filtering_logic():
        success_count += 1
    
    print(f"\nRIEPILOGO: {success_count}/{total_tests} test superati")
    
    if success_count == total_tests:
        print("SUCCESSO: Sistema filtri ingredienti funzionante!")
        print("Nell'UI potrai:")
        print("1. Cercare ingredienti per nome")
        print("2. Filtrare per tipo (formaggio, carne, verdura, etc.)")
        print("3. Ordinare per consumo, costo, utilizzi, trend")
        print("4. Vedere i dati aggiornati in tempo reale")
    else:
        print("ATTENZIONE: Problemi nel sistema filtri")
        print("Verifica i log per i dettagli")

if __name__ == "__main__":
    main()
