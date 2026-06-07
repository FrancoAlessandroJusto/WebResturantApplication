#!/usr/bin/env python3
import sqlite3
from db import get_conn

def add_people_cover_fields():
    """Aggiunge i campi numero_persone e coperto alla tabella ordini"""
    conn = get_conn()
    
    try:
        # Controlla se le colonne esistono già
        cursor = conn.execute("PRAGMA table_info(ordini)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print("Colonne attuali nella tabella ordini:")
        for col in columns:
            print(f"  - {col}")
        
        # Aggiunge numero_persone se non esiste
        if 'numero_persone' not in columns:
            conn.execute("ALTER TABLE ordini ADD COLUMN numero_persone INTEGER DEFAULT 1")
            print("Aggiunta colonna 'numero_persone'")
        else:
            print("Colonna 'numero_persone' gia esistente")
        
        # Aggiunge coperto se non esiste
        if 'coperto' not in columns:
            conn.execute("ALTER TABLE ordini ADD COLUMN coperto REAL DEFAULT 0.0")
            print("Aggiunta colonna 'coperto'")
        else:
            print("Colonna 'coperto' gia esistente")
        
        conn.commit()
        print("Database aggiornato con successo!")
        
    except Exception as e:
        print(f"Errore: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_people_cover_fields()
