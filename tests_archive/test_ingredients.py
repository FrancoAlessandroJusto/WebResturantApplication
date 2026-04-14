import requests

# Test API ingredienti
response = requests.get('http://127.0.0.1:8000/analytics/ingredients?periodo=today')
print(f"Status: {response.status_code}")

if response.ok:
    data = response.json()
    ingredients = data.get('ingredienti_analytics', [])
    print(f'Ingredienti trovati: {len(ingredients)}')
    
    if ingredients:
        print("Primi 3 ingredienti:")
        for i, ing in enumerate(ingredients[:3], 1):
            print(f"  {i}. {ing.get('ingrediente')} - €{ing.get('costo_totale', 0):.2f}")
else:
    print(f"Errore: {response.text}")
