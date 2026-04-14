# =========================
# TEST MINIMO GET /ingredienti
# =========================

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Aggiungi il percorso del progetto
sys.path.append(str(Path(__file__).parent))

try:
    from main import app
    APP_AVAILABLE = True
except ImportError as e:
    print(f"ATTENZIONE: Impossibile importare l'app: {e}")
    APP_AVAILABLE = False

@pytest.fixture
def client():
    """Test client fixture"""
    if not APP_AVAILABLE:
        pytest.skip("App non disponibile")
    
    with TestClient(app) as test_client:
        yield test_client

def test_get_ingredienti_basic(client):
    """Test minimo per GET /ingredienti
    
    Verifica solo:
    - Endpoint esiste e risponde
    - Status code 200
    - Risposta è una lista JSON
    
    Non verifica:
    - Contenuto specifico dei dati
    - Struttura dei singoli oggetti
    - Dati di dominio specifici
    """
    response = client.get("/ingredienti")
    
    # Verifica esistenza endpoint e risposta corretta
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Verifica formato base JSON
    data = response.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    
    # NOTA: Non verifichiamo il contenuto della lista
    # perché i dati nel database non sono verificati

if __name__ == "__main__":
    print("🧪 TEST MINIMO GET /ingredienti")
    print("=" * 35)
    
    if not APP_AVAILABLE:
        print("❌ App non disponibile")
        sys.exit(1)
    
    pytest.main([__file__, "-v", "--tb=short"])
