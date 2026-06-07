#!/usr/bin/env python3
"""
Migration per aggiungere tabella delle modifiche ingredienti negli ordini
"""

import sqlite3
from db import get_conn

def create_order_modifications_table():
    """Crea tabella per memorizzare le modifiche ingredienti negli ordini"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        # Crea tabella per le modifiche ingredienti negli ordini
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordine_dettagli_modifiche (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ordine_dettagli_id INTEGER NOT NULL,
                ingrediente_id INTEGER NOT NULL,
                azione TEXT NOT NULL CHECK(azione IN ('aggiunto', 'rimosso')),
                prezzo_modifica REAL NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ordine_dettagli_id) REFERENCES ordine_dettagli(id) ON DELETE CASCADE,
                FOREIGN KEY (ingrediente_id) REFERENCES ingredienti(id) ON DELETE CASCADE
            )
        """)
        
        # Aggiunge colonna prezzo_personalizzato a ordine_dettagli
        cursor.execute("""
            ALTER TABLE ordine_dettagli 
            ADD COLUMN prezzo_personalizzato REAL DEFAULT NULL
        """)
        
        # Aggiunge colonna note_modifiche a ordine_dettagli
        cursor.execute("""
            ALTER TABLE ordine_dettagli 
            ADD COLUMN note_modifiche TEXT DEFAULT NULL
        """)
        
        conn.commit()
        print("SUCCESSO: Tabella ordine_dettagli_modifiche creata")
        print("SUCCESSO: Colonne prezzo_personalizzato e note_modifiche aggiunte")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("INFO: Colonne gia esistenti, saltate")
        else:
            print(f"ERRORE: {e}")
            conn.rollback()
            return False
    
    return True

def setup_ingredient_price_rules():
    """Configura le regole di prezzo per le modifiche ingredienti"""
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        # Crea tabella per le regole prezzo modifiche
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regole_prezzo_modifiche (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_ingrediente TEXT NOT NULL,
                prezzo_aggiunta REAL NOT NULL,
                prezzo_rimozione REAL NOT NULL DEFAULT 0,
                attiva INTEGER NOT NULL DEFAULT 1,
                UNIQUE(tipo_ingrediente)
            )
        """)
        
        # Inserisce le regole base
        regole = [
            ('formaggio', 1.5, 0.5),    # Aggiunta: 1.5€, Rimozione: 0.5€
            ('carne', 2.0, 1.0),        # Aggiunta: 2.0€, Rimozione: 1.0€
            ('verdura', 1.0, 0.3),      # Aggiunta: 1.0€, Rimozione: 0.3€
            ('salsa', 0.0, 0.0),        # Aggiunta: gratis, Rimozione: gratis
            ('altro', 1.0, 0.5)         # Default
        ]
        
        for tipo, prezzo_aggiunta, prezzo_rimozione in regole:
            cursor.execute("""
                INSERT OR IGNORE INTO regole_prezzo_modifiche 
                (tipo_ingrediente, prezzo_aggiunta, prezzo_rimozione) 
                VALUES (?, ?, ?)
            """, (tipo, prezzo_aggiunta, prezzo_rimozione))
        
        conn.commit()
        print("SUCCESSO: Regole prezzo configurate")
        
    except Exception as e:
        print(f"ERRORE: {e}")
        conn.rollback()
        return False
    
    return True

def main():
    print("MIGRATION DATABASE - Modifiche Ingredienti Ordini")
    print("=" * 50)
    
    # Crea tabella modifiche
    if create_order_modifications_table():
        print("OK Tabella modifiche creata")
    else:
        print("ERRORE creazione tabella")
        return
    
    # Configura regole prezzo
    if setup_ingredient_price_rules():
        print("OK Regole prezzo configurate")
    else:
        print("ERRORE configurazione regole")
        return
    
    print("\nSUCCESSO Migration completata!")
    print("Ora puoi gestire le modifiche ingredienti negli ordini")

if __name__ == "__main__":
    main()
