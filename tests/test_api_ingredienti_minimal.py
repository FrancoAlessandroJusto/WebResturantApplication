# =========================
# SUITE DI TEST MINIMALE API INGREDIENTI
# =========================

import pytest
import sqlite3
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Aggiungi il percorso del progetto
sys.path.append(str(Path(__file__).parent))

# Import dell'app
try:
    from main import app
    from core.database import get_conn
    APP_AVAILABLE = True
except ImportError as e:
    print(f"ATTENZIONE: Impossibile importare l'app: {e}")
    APP_AVAILABLE = False

# =========================
# UTILITIES
# =========================

def get_database_record(ingrediente_id: int):
    """Recupera record diretto dal database"""
    if not APP_AVAILABLE:
        return None
        
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM ingredienti WHERE id = ?", 
        (ingrediente_id,)
    ).fetchone()
    conn.close()
    
    return dict(row) if row else None

def cleanup_test_data():
    """Pulisce dati di test dal database"""
    if not APP_AVAILABLE:
        return
        
    conn = get_conn()
    # Elimina ingredienti di test
    conn.execute(
        "DELETE FROM ingredienti WHERE nome LIKE '%_test' OR nome LIKE 'Test %'"
    )
    conn.commit()
    conn.close()

# =========================
# FIXTURES
# =========================

@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup e teardown automatici per ogni test"""
    # Cleanup prima del test
    cleanup_test_data()
    yield
    # Cleanup dopo il test
    cleanup_test_data()

@pytest.fixture
def client():
    """Test client fixture"""
    if not APP_AVAILABLE:
        pytest.skip("App non disponibile")
    
    with TestClient(app) as test_client:
        yield test_client

# =========================
# TEST ENDPOINT
# =========================

def test_get_ingredienti_success(client):
    """GET /ingredienti restituisce 200 e lista JSON"""
    response = client.get("/ingredienti")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"

def test_get_ingredienti_by_id_not_found(client):
    """GET /ingredienti/{id} restituisce 404 se l'id non esiste"""
    response = client.get("/ingredienti/99999")
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    assert "non trovato" in response.json()["detail"]

def test_create_ingrediente_success(client):
    """POST /ingredienti crea un ingrediente valido con dati compatibili col database"""
    ingrediente_data = {
        "nome": "Test Ingrediente",
        "tipo": "altro",  # Valore compatibile con CHECK constraint
        "costo_unitario": 10.0,
        "unita_riferimento": "kg",
        "quantita_riferimento": 1.0
    }
    
    response = client.post("/ingredienti", json=ingrediente_data)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "id" in data
    assert data["nome"] == ingrediente_data["nome"]
    assert data["tipo"] == ingrediente_data["tipo"]
    assert data["costo_unitario"] == ingrediente_data["costo_unitario"]

def test_create_ingrediente_duplicate(client):
    """POST /ingredienti con nome duplicato restituisce 409"""
    # Prima crea un ingrediente
    ingrediente_data = {
        "nome": "Test Duplicate",
        "tipo": "altro",
        "costo_unitario": 5.0,
        "unita_riferimento": "pz",
        "quantita_riferimento": 1.0
    }
    
    response1 = client.post("/ingredienti", json=ingrediente_data)
    assert response1.status_code == 200
    
    # Tenta creare duplicato
    response2 = client.post("/ingredienti", json=ingrediente_data)
    
    assert response2.status_code == 409, f"Expected 409 for duplicate, got {response2.status_code}"
    assert "già esistente" in response2.json()["detail"]

def test_update_ingrediente_partial(client):
    """PUT /ingredienti/{id} aggiorna solo i campi passati"""
    # Prima crea un ingrediente
    create_data = {
        "nome": "Test Update",
        "tipo": "altro",
        "costo_unitario": 8.0,
        "unita_riferimento": "kg",
        "quantita_riferimento": 1.0
    }
    
    create_response = client.post("/ingredienti", json=create_data)
    ingrediente_id = create_response.json()["id"]
    
    # Aggiorna solo il costo
    update_data = {
        "costo_unitario": 12.0
    }
    
    response = client.put(f"/ingredienti/{ingrediente_id}", json=update_data)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    updated_data = response.json()
    assert updated_data["costo_unitario"] == 12.0
    assert updated_data["nome"] == "Test Update"  # Non dovrebbe cambiare
    assert updated_data["tipo"] == "altro"  # Non dovrebbe cambiare

def test_update_ingrediente_empty_body(client):
    """PUT /ingredienti/{id} con body vuoto restituisce errore"""
    # Prima crea un ingrediente
    create_data = {
        "nome": "Test Empty",
        "tipo": "altro",
        "costo_unitario": 3.0,
        "unita_riferimento": "pz",
        "quantita_riferimento": 1.0
    }
    
    create_response = client.post("/ingredienti", json=create_data)
    ingrediente_id = create_response.json()["id"]
    
    # Tenta aggiornamento con body vuoto
    response = client.put(f"/ingredienti/{ingrediente_id}", json={})
    
    assert response.status_code == 400, f"Expected 400 for empty body, got {response.status_code}"
    assert "Nessun dato fornito" in response.json()["detail"]

def test_delete_soft_delete(client):
    """DELETE /ingredienti/{id} effettua soft delete"""
    # Prima crea un ingrediente
    create_data = {
        "nome": "Test Delete",
        "tipo": "altro",
        "costo_unitario": 7.0,
        "unita_riferimento": "kg",
        "quantita_riferimento": 1.0
    }
    
    create_response = client.post("/ingredienti", json=create_data)
    ingrediente_id = create_response.json()["id"]
    
    # Verifica che esista prima del delete
    record_before = get_database_record(ingrediente_id)
    assert record_before is not None, "Record dovrebbe esistere prima del delete"
    assert record_before["attiva"] == 1, "Record dovrebbe essere attivo prima del delete"
    
    # Esegui soft delete
    response = client.delete(f"/ingredienti/{ingrediente_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Verifica che non sia più visibile nelle API
    get_response = client.get("/ingredienti")
    ingredienti_attivi = [ing for ing in get_response.json() if ing["id"] == ingrediente_id]
    assert len(ingredienti_attivi) == 0, "Ingrediente eliminato non dovrebbe apparire in GET /ingredienti"

# =========================
# TEST SOFT DELETE SU DATABASE
# =========================

def test_soft_delete_database_verification(client):
    """Verifica SQL diretta che dopo il delete: la riga esiste ancora e attiva = 0"""
    # Prima crea un ingrediente
    create_data = {
        "nome": "Test Database Verify",
        "tipo": "altro",
        "costo_unitario": 15.0,
        "unita_riferimento": "kg",
        "quantita_riferimento": 1.0
    }
    
    create_response = client.post("/ingredienti", json=create_data)
    ingrediente_id = create_response.json()["id"]
    
    # Esegui soft delete
    delete_response = client.delete(f"/ingredienti/{ingrediente_id}")
    assert delete_response.status_code == 200
    
    # Verifica diretta sul database
    record_after = get_database_record(ingrediente_id)
    
    # La riga dovrebbe esistere ancora
    assert record_after is not None, "La riga nel database dovrebbe esistere ancora dopo soft delete"
    
    # Il campo attiva dovrebbe essere 0
    assert record_after["attiva"] == 0, f"Il campo attiva dovrebbe essere 0, è {record_after['attiva']}"
    
    # Altri campi dovrebbero rimanere invariati
    assert record_after["nome"] == "Test Database Verify"
    assert record_after["tipo"] == "altro"

# =========================
# ESECUZIONE
# =========================

if __name__ == "__main__":
    print("🧪 ESECUZIONE TEST MINIMI API INGREDIENTI")
    print("=" * 45)
    
    if not APP_AVAILABLE:
        print("❌ App non disponibile - impossibile eseguire i test")
        sys.exit(1)
    
    # Esegui i test
    pytest.main([__file__, "-v", "--tb=short"])
