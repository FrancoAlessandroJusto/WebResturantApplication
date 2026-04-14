# =========================
# TEST AUTOMATICI API INGREDIENTI
# =========================

import pytest
import sqlite3
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from typing import Dict, Any

# Aggiungi il percorso del progetto al sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Import dell'app FastAPI
try:
    from main import app
    from core.database import get_conn, DatabaseManager
    from models import Ingrediente
    APP_AVAILABLE = True
except ImportError as e:
    print(f"ATTENZIONE: Impossibile importare l'app: {e}")
    APP_AVAILABLE = False

# =========================
# FIXTURES E UTILITIES
# =========================

@pytest.fixture(scope="session")
def test_client():
    """Fixture for TestClient"""
    if not APP_AVAILABLE:
        pytest.skip("App non disponibile")
    
    # Inizializza database di test
    init_test_database()
    
    with TestClient(app) as client:
        yield client
    
    # Cleanup database di test
    cleanup_test_database()

def init_test_database():
    """Inizializza database di test pulito"""
    if not APP_AVAILABLE:
        return
        
    conn = get_conn()
    
    # Pulisce tabella ingredienti
    conn.execute("DELETE FROM ingredienti")
    
    # Inserisce dati di test
    test_ingredienti = [
        ("Mozzarella", "latticino", 5.0, "kg", 1.0),
        ("Pomodoro", "verdura", 2.0, "kg", 1.0),
        ("Basilico", "erba", 1.0, "pz", 0.05)
    ]
    
    for nome, tipo, costo, unita, quantita in test_ingredienti:
        conn.execute(
            "INSERT INTO ingredienti (nome, tipo, costo_unitario, unita_riferimento, quantita_riferimento, attiva) VALUES (?, ?, ?, ?, ?, 1)",
            (nome, tipo, costo, unita, quantita)
        )
    
    conn.commit()
    conn.close()

def cleanup_test_database():
    """Pulisce database di test"""
    if not APP_AVAILABLE:
        return
        
    conn = get_conn()
    conn.execute("DELETE FROM ingredienti")
    conn.commit()
    conn.close()

def get_database_record(ingrediente_id: int) -> Dict[str, Any]:
    """Recupera record diretto dal database"""
    if not APP_AVAILABLE:
        return {}
        
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM ingredienti WHERE id = ?", 
        (ingrediente_id,)
    ).fetchone()
    conn.close()
    
    return dict(row) if row else {}

# =========================
# TEST STRUTTURALI
# =========================

def test_router_registration():
    """Verifica che il router /ingredienti sia registrato"""
    if not APP_AVAILABLE:
        pytest.skip("App non disponibile")
    
    # Controlla che il router sia registrato nell'app
    routes = [route.path for route in app.routes]
    assert "/ingredienti" in routes, "Router /ingredienti non registrato"
    
    # Controlla i singoli endpoint
    expected_endpoints = [
        "/ingredienti",
        "/ingredienti/{ingrediente_id}"
    ]
    
    for endpoint in expected_endpoints:
        assert endpoint in routes, f"Endpoint {endpoint} non registrato"

def test_endpoint_methods():
    """Verifica che tutti i metodi HTTP siano disponibili"""
    if not APP_AVAILABLE:
        pytest.skip("App non disponibile")
    
    client = TestClient(app)
    
    # Test OPTIONS per verificare metodi disponibili
    response = client.options("/ingredienti")
    assert response.status_code in [200, 405]  # 405 se OPTIONS non implementato
    
    # Verifica esistenza endpoint tramite richieste
    endpoints_methods = [
        ("/ingredienti", ["GET", "POST"]),
        ("/ingredienti/999", ["GET", "PUT", "DELETE"])
    ]
    
    for endpoint, methods in endpoints_methods:
        for method in methods:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            # Non deve restituire 404 (endpoint non trovato)
            assert response.status_code != 404, f"Endpoint {endpoint} non trovato per metodo {method}"

# =========================
# TEST FUNZIONALI
# =========================

def test_get_ingredienti_success(test_client):
    """Test GET /ingredienti - restituisce 200 e lista JSON"""
    response = test_client.get("/ingredienti")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    
    # Verifica che ci siano ingredienti di test
    assert len(data) >= 3, f"Expected at least 3 ingredients, got {len(data)}"

def test_get_ingredienti_structure(test_client):
    """Test struttura risposta GET /ingredienti"""
    response = test_client.get("/ingredienti")
    data = response.json()
    
    if len(data) > 0:
        ingrediente = data[0]
        expected_fields = ["id", "nome", "tipo", "costo_unitario", "unita_riferimento", "quantita_riferimento", "attiva"]
        
        for field in expected_fields:
            assert field in ingrediente, f"Field {field} missing from response"

def test_create_ingrediente_success(test_client):
    """Test POST /ingredienti - creazione ingrediente valido"""
    ingrediente_data = {
        "nome": "Salame Test",
        "tipo": "salume",
        "costo_unitario": 15.0,
        "unita_riferimento": "kg",
        "quantita_riferimento": 1.0
    }
    
    response = test_client.post("/ingredienti", json=ingrediente_data)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "id" in data, "ID missing from response"
    assert data["nome"] == ingrediente_data["nome"], "Nome non corrispondente"
    assert data["tipo"] == ingrediente_data["tipo"], "Tipo non corrispondente"
    assert data["costo_unitario"] == ingrediente_data["costo_unitario"], "Costo non corrispondente"

def test_create_ingrediente_duplicate(test_client):
    """Test POST duplicato - deve restituire 409"""
    ingrediente_data = {
        "nome": "Mozzarella",  # Già esistente nel database di test
        "tipo": "latticino",
        "costo_unitario": 5.0,
        "unita_riferimento": "kg",
        "quantita_riferimento": 1.0
    }
    
    response = test_client.post("/ingredienti", json=ingrediente_data)
    
    assert response.status_code == 409, f"Expected 409 for duplicate, got {response.status_code}"
    assert "già esistente" in response.json()["detail"], "Error message non corretto"

def test_update_ingrediente_partial(test_client):
    """Test PUT aggiornamento parziale - solo campo specificato"""
    # Prima crea un ingrediente
    create_data = {
        "nome": "Provolone Test",
        "tipo": "latticino",
        "costo_unitario": 12.0,
        "unita_riferimento": "kg",
        "quantita_riferimento": 1.0
    }
    
    create_response = test_client.post("/ingredienti", json=create_data)
    ingrediente_id = create_response.json()["id"]
    
    # Aggiorna solo il costo
    update_data = {
        "costo_unitario": 14.0
    }
    
    response = test_client.put(f"/ingredienti/{ingrediente_id}", json=update_data)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    updated_data = response.json()
    assert updated_data["costo_unitario"] == 14.0, "Costo non aggiornato"
    assert updated_data["nome"] == "Provolone Test", "Nome non dovrebbe cambiare"
    assert updated_data["tipo"] == "latticino", "Tipo non dovrebbe cambiare"

def test_update_ingrediente_empty_body(test_client):
    """Test PUT con body vuoto - deve restituire errore"""
    # Prima crea un ingrediente
    create_data = {
        "nome": "Ricotta Test",
        "tipo": "latticino",
        "costo_unitario": 8.0,
        "unita_riferimento": "kg",
        "quantita_riferimento": 1.0
    }
    
    create_response = test_client.post("/ingredienti", json=create_data)
    ingrediente_id = create_response.json()["id"]
    
    # Tenta aggiornamento con body vuoto
    response = test_client.put(f"/ingredienti/{ingrediente_id}", json={})
    
    assert response.status_code == 400, f"Expected 400 for empty body, got {response.status_code}"
    assert "Nessun dato fornito" in response.json()["detail"], "Error message non corretto"

def test_delete_soft_delete(test_client):
    """Test DELETE soft delete - non elimina fisicamente il record"""
    # Prima crea un ingrediente
    create_data = {
        "nome": "Gorgonzola Test",
        "tipo": "latticino",
        "costo_unitario": 18.0,
        "unita_riferimento": "kg",
        "quantita_riferimento": 1.0
    }
    
    create_response = test_client.post("/ingredienti", json=create_data)
    ingrediente_id = create_response.json()["id"]
    
    # Verifica che esista prima del delete
    record_before = get_database_record(ingrediente_id)
    assert record_before["attiva"] == 1, "Ingrediente dovrebbe essere attivo prima del delete"
    
    # Esegui soft delete
    response = test_client.delete(f"/ingredienti/{ingrediente_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Verifica che il record esista ancora nel database
    record_after = get_database_record(ingrediente_id)
    assert record_after is not None, "Record non dovrebbe essere eliminato fisicamente"
    assert record_after["attiva"] == 0, "Campo attiva dovrebbe essere 0 dopo soft delete"
    
    # Verifica che non sia più visibile nelle API
    get_response = test_client.get("/ingredienti")
    ingredienti_attivi = [ing for ing in get_response.json() if ing["id"] == ingrediente_id]
    assert len(ingredienti_attivi) == 0, "Ingrediente eliminato non dovrebbe apparire in GET /ingredienti"

# =========================
# TEST DI INTEGRAZIONE
# =========================

def test_database_manager_usage():
    """Verifica che il router utilizzi DatabaseManager.get_connection()"""
    if not APP_AVAILABLE:
        pytest.skip("App non disponibile")
    
    # Legge il codice sorgente del router
    router_file = Path(__file__).parent.parent / "routes" / "api" / "ingredienti_new.py"
    
    if not router_file.exists():
        pytest.skip("File router non trovato")
    
    with open(router_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert "DatabaseManager.get_connection()" in content, "DatabaseManager.get_connection() non utilizzato"
    assert "with DatabaseManager.get_connection()" in content, "Context manager non utilizzato"

def test_model_methods_usage():
    """Verifica che il router utilizzi i metodi del model"""
    if not APP_AVAILABLE:
        pytest.skip("App non disponibile")
    
    router_file = Path(__file__).parent.parent / "routes" / "api" / "ingredienti_new.py"
    
    if not router_file.exists():
        pytest.skip("File router non trovato")
    
    with open(router_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_methods = [
        "Ingrediente.get_all()",
        "Ingrediente.create(",
        "Ingrediente.from_db(",
        ".to_dict()"
    ]
    
    for method in required_methods:
        assert method in content, f"Metodo {method} non utilizzato"

# =========================
# TEST PERFORMANCE E LIMITE
# =========================

def test_get_ingredienti_performance(test_client):
    """Test performance GET /ingredienti"""
    import time
    
    start_time = time.time()
    response = test_client.get("/ingredienti")
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 1.0, f"Request too slow: {end_time - start_time}s"

def test_concurrent_requests(test_client):
    """Test richieste concorrenti"""
    import threading
    import time
    
    results = []
    
    def make_request():
        response = test_client.get("/ingredienti")
        results.append(response.status_code)
    
    # Crea 10 richieste concorrenti
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Attendi che tutte terminino
    for thread in threads:
        thread.join()
    
    # Verifica che tutte abbiano avuto successo
    assert all(status == 200 for status in results), f"Some requests failed: {results}"

# =========================
# MAIN ESECUZIONE
# =========================

if __name__ == "__main__":
    print("🧪 ESECUZIONE TEST API INGREDIENTI")
    print("=" * 50)
    
    if not APP_AVAILABLE:
        print("❌ App non disponibile - impossibile eseguire i test")
        sys.exit(1)
    
    # Esegui i test
    pytest.main([__file__, "-v", "--tb=short"])
