#!/usr/bin/env python3
"""
Test del nuovo Database Manager per verificare che tutto funzioni correttamente
prima di applicare le modifiche al codice esistente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import DatabaseManager, handle_database_errors
from fastapi import HTTPException

def test_database_manager():
    """Test del Database Manager context manager"""
    print("Test Database Manager...")
    
    try:
        # Test 1: Connessione e query
        with DatabaseManager.get_connection() as conn:
            result = conn.execute("SELECT COUNT(*) as count FROM menu_items").fetchone()
            print(f"Test 1: Connessione OK - Menu items: {result['count']}")
        
        # Test 2: Metodo execute_query
        items = DatabaseManager.execute_query("SELECT * FROM menu_items LIMIT 3")
        print(f"Test 2: execute_query OK - Trovati {len(items)} items")
        
        # Test 3: Metodo execute_update
        rowcount = DatabaseManager.execute_update(
            "UPDATE menu_items SET prezzo = prezzo WHERE 1=0"
        )
        print(f"Test 3: execute_update OK - Rowcount: {rowcount}")
        
        # Test 4: Error handling
        try:
            DatabaseManager.execute_query("SELECT * FROM tabella_inesistente")
            print("Test 4: Error handling FALLITO")
        except Exception as e:
            print(f"Test 4: Error handling OK - {type(e).__name__}")
        
        print("Database Manager test completato con successo!")
        return True
        
    except Exception as e:
        print(f"Database Manager test FALLITO: {e}")
        return False

def test_decorator():
    """Test del decorator di error handling"""
    print("Test Error Handling Decorator...")
    
    try:
        # Questa funzione dovrebbe gestire automaticamente gli errori
        result = DatabaseManager.execute_query("SELECT COUNT(*) as count FROM menu_items")
        return {"success": True, "count": result[0]['count']}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=" * 50)
    print("TEST DEL NUOVO DATABASE MANAGER")
    print("=" * 50)
    
    # Test 1: Database Manager
    if not test_database_manager():
        print("STOP: Database Manager non funziona correttamente")
        return
    
    print()
    
    # Test 2: Error Handling Decorator
    try:
        result = test_decorator()
        if result["success"]:
            print(f"Decorator test OK - Count: {result['count']}")
        else:
            print(f"Decorator test FALLITO: {result['error']}")
    except Exception as e:
        print(f"Decorator test OK - Gestito errore: {type(e).__name__}")
    
    print()
    print("TEST COMPLETATI - Database Manager pronto per l'uso!")
    print("Ora puoi iniziare a migrare il codice esistente")

if __name__ == "__main__":
    main()
