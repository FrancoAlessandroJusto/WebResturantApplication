#!/usr/bin/env python3
"""
Script per aggiungere il campo 'served' alla tabella ordine_dettagli
"""

import sqlite3
import sys
from pathlib import Path

# Aggiungi la directory del progetto al path
sys.path.append(str(Path(__file__).parent))

def add_served_field():
    """Aggiunge il campo served alla tabella ordine_dettagli"""
    
    try:
        from db import get_conn
        conn = get_conn()
        cursor = conn.cursor()
        
        print("Aggiunta campo 'served' alla tabella ordine_dettagli...")
        
        # Aggiungi il campo served se non esiste
        try:
            cursor.execute("""
                ALTER TABLE ordine_dettagli 
                ADD COLUMN served INTEGER DEFAULT 0 CHECK(served IN (0,1))
            """)
            print("Campo 'served' aggiunto con successo")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("Campo 'served' esiste gia'")
            else:
                raise e
        
        # Inizializza tutti i record esistenti come non serviti (served = 0)
        cursor.execute("""
            UPDATE ordine_dettagli 
            SET served = 0 
            WHERE served IS NULL
        """)
        
        conn.commit()
        conn.close()
        
        print("Database aggiornato con successo")
        return True
        
    except Exception as e:
        print(f"Errore durante l'aggiornamento: {e}")
        return False

if __name__ == "__main__":
    print("Aggiornamento database per gestione stato servito articoli")
    print("=" * 50)
    
    success = add_served_field()
    
    if success:
        print("\nAggiornamento completato!")
        print("Ora puoi gestire gli stati 'servito' per gli articoli degli ordini")
    else:
        print("\nAggiornamento fallito!")
        sys.exit(1)
