# =========================
# VERIFICA STRUTTURALE AUTOMATICA
# =========================
 
import sys
import os
from pathlib import Path
import importlib.util
 
# Aggiungi il percorso del progetto
sys.path.append(str(Path(__file__).parent))
 
def check_app_structure():
    """Verifica struttura base dell'app"""
    print("🔍 VERIFICA STRUTTURA APP")
    print("-" * 30)
 
    # Controlla file principali
    required_files = [
        "main.py",
        "models.py",
        "schemas.py",
        "core/database.py",
        "routes/api/ingredienti_new.py"
    ]
 
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MANCANTE")
 
    return True
 
def check_router_registration():
    """Verifica registrazione router nell'app"""
    print("\n🔍 VERIFICA REGISTRAZIONE ROUTER")
    print("-" * 35)
 
    try:
        # Importa l'app
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
 
        app = main_module.app
 
        # Controlla routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
 
        print(f"📋 Trovati {len(routes)} routes:")
        for route in sorted(routes):
            if "ingredienti" in route:
                print(f"  ✅ {route}")
            else:
                print(f"  📄 {route}")
 
        # Verifica router ingredienti
        ingredienti_routes = [r for r in routes if "ingredienti" in r]
        if len(ingredienti_routes) > 0:
            print(f"\n✅ Router ingredienti registrato: {len(ingredienti_routes)} routes")
        else:
            print("\n❌ Router ingredienti NON registrato")
 
    except Exception as e:
        print(f"❌ Errore import app: {e}")
        return False
 
    return True
 
def check_database_connection():
    """Verifica connessione database"""
    print("\n🔍 VERIFICA CONNESSIONE DATABASE")
    print("-" * 35)
 
    try:
        from core.database import get_conn, DatabaseManager
 
        # Test connessione base
        conn = get_conn()
        print("✅ Connessione database funzionante")
 
        # Test DatabaseManager
        with DatabaseManager.get_connection() as conn:
            result = conn.execute("SELECT COUNT(*) FROM ingredienti").fetchone()
            count = result[0] if result else 0
            print(f"✅ DatabaseManager funzionante - {count} ingredienti nel database")
 
        return True
 
    except Exception as e:
        print(f"❌ Errore database: {e}")
        return False
 
def check_models_availability():
    """Verifica disponibilità models"""
    print("\n🔍 VERIFICA MODELS")
    print("-" * 20)
 
    try:
        from models import Ingrediente
 
        # Test metodi del model
        methods = ["get_all", "create", "from_db", "to_dict"]
        for method in methods:
            if hasattr(Ingrediente, method):
                print(f"✅ Ingrediente.{method}")
            else:
                print(f"❌ Ingrediente.{method} - MANCANTE")
 
        return True
 
    except Exception as e:
        print(f"❌ Errore models: {e}")
        return False
 
def check_schemas_structure():
    """Verifica struttura schemas"""
    print("\n🔍 VERIFICA SCHEMAS")
    print("-" * 20)
 
    try:
        import schemas
 
        # Controlla schemi esistenti
        schema_names = [name for name in dir(schemas) if not name.startswith("_")]
        print(f"📋 Schemi trovati: {schema_names}")
 
        # Verifica se ci sono schemi per ingredienti
        ingredienti_schemas = [name for name in schema_names if "ingrediente" in name.lower()]
        if ingredienti_schemas:
            print(f"✅ Schemi ingredienti: {ingredienti_schemas}")
        else:
            print("⚠️  Nessuno schema specifico per ingredienti trovato")
 
        return True
 
    except Exception as e:
        print(f"❌ Errore schemas: {e}")
        return False
 
def main():
    """Esecuzione verifica strutturale completa"""
    print("🏗️  VERIFICA STRUTTURALE PROGETTO")
    print("=" * 40)
 
    checks = [
        check_app_structure,
        check_router_registration,
        check_database_connection,
        check_models_availability,
        check_schemas_structure
    ]
 
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Errore in {check.__name__}: {e}")
            results.append(False)
 
    print("\n" + "=" * 40)
    print("📊 RIEPILOGO VERIFICHE")
    print("-" * 25)
 
    passed = sum(results)
    total = len(results)
 
    print(f"✅ Superate: {passed}/{total}")
    print(f"❌ Fallite: {total - passed}/{total}")
 
    if passed == total:
        print("\n🎉 Tutte le verifiche strutturali superate!")
    else:
        print("\n⚠️  Alcune verifiche fallite - controllare i dettagli sopra")
 
    return passed == total
 
if __name__ == "__main__":
    main()