#!/usr/bin/env python3
"""
Script per creare la tabella pagamenti e gestire le transazioni
"""

import sqlite3
import sys
from pathlib import Path

# Aggiungi la directory del progetto al path
sys.path.append(str(Path(__file__).parent))

def create_payments_table():
    """Crea la tabella pagamenti se non esiste"""
    
    try:
        from db import get_conn
        conn = get_conn()
        cursor = conn.cursor()
        
        print("Creazione tabella pagamenti...")
        
        # Crea tabella pagamenti
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagamenti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ordine_id INTEGER NOT NULL,
                importo REAL NOT NULL CHECK(importo >= 0),
                metodo_pagamento TEXT NOT NULL CHECK(metodo_pagamento IN ('carta', 'contanti')),
                data_ora DATETIME DEFAULT CURRENT_TIMESTAMP,
                operatore TEXT DEFAULT 'system',
                note TEXT,
                FOREIGN KEY (ordine_id) REFERENCES ordini(id) ON DELETE CASCADE
            )
        """)
        
        print("Tabella pagamenti creata con successo")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Errore creazione tabella pagamenti: {e}")
        return False

if __name__ == "__main__":
    print("Creazione tabella pagamenti per gestione transazioni")
    print("=" * 50)
    
    success = create_payments_table()
    
    if success:
        print("\nTabella pagamenti creata con successo!")
        print("Ora puoi gestire i pagamenti carta/contanti")
    else:
        print("\nCreazione tabella fallita!")
        sys.exit(1)
