# =========================
# DATABASE MANAGER - Centralizzato e Sicuro
# =========================

import sqlite3
import logging
import os
from contextlib import contextmanager
from functools import wraps
from typing import Generator, Any, Callable

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'pizzeria.db')

def get_conn() -> sqlite3.Connection:
    """Ottieni connessione al database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Inizializza lo schema del database"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Tabella ingredienti
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ingredienti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        tipo TEXT DEFAULT 'altro' CHECK(tipo IN ('base', 'salsa', 'formaggio', 'carne', 'verdura', 'premade', 'altro')),
        costo_unitario REAL NOT NULL CHECK(costo_unitario >= 0),
        unita_riferimento TEXT DEFAULT 'pz' CHECK(unita_riferimento IN ('g', 'ml', 'pz', 'kg', 'l')),
        quantita_riferimento REAL NOT NULL DEFAULT 1 CHECK(quantita_riferimento > 0),
        attiva INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))
    )
    """)
    
    # Tabella menu_items
    cur.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        prezzo REAL NOT NULL CHECK(prezzo >= 0),
        categoria TEXT DEFAULT 'Pizza',
        attiva INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))
    )
    """)
    
    # Tabella di collegamento
    cur.execute("""
    CREATE TABLE IF NOT EXISTS menu_item_ingredienti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_item_id INTEGER NOT NULL,
        ingrediente_id INTEGER NOT NULL,
        quantita REAL NOT NULL CHECK(quantita > 0),
        FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
        FOREIGN KEY (ingrediente_id) REFERENCES ingredienti(id) ON DELETE CASCADE,
        UNIQUE(menu_item_id, ingrediente_id)
    )
    """)
    
    # Tabella ordini
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ordini (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_tavolo INTEGER NOT NULL,
        data_ora DATETIME DEFAULT CURRENT_TIMESTAMP,
        stato TEXT DEFAULT 'in_corso' CHECK(stato IN ('in_corso', 'completato', 'annullato')),
        totale REAL NOT NULL DEFAULT 0 CHECK(totale >= 0),
        numero_persone INTEGER DEFAULT 1 CHECK(numero_persone > 0),
        coperto REAL DEFAULT 0 CHECK(coperto >= 0),
        metodo_pagamento TEXT,
        data_pagamento DATETIME
    )
    """)
    
    # Tabella dettagli ordini
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ordine_dettagli (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ordine_id INTEGER NOT NULL,
        pizza_id INTEGER NOT NULL,
        quantita INTEGER NOT NULL CHECK(quantita > 0),
        note TEXT,
        prezzo_unitario REAL NOT NULL CHECK(prezzo_unitario >= 0),
        prezzo_personalizzato REAL,
        served INTEGER DEFAULT 0 CHECK(served IN (0,1)),
        note_modifiche TEXT,
        FOREIGN KEY (ordine_id) REFERENCES ordini(id) ON DELETE CASCADE,
        FOREIGN KEY (pizza_id) REFERENCES menu_items(id)
    )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database inizializzato con successo")

class DatabaseManager:
    """Gestore centralizzato delle connessioni database con error handling"""
    
    @staticmethod
    @contextmanager
    def get_connection() -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager per connessioni sicure al database.
        
        Garantisce che la connessione sia sempre chiusa,
        anche in caso di eccezioni.
        
        Usage:
            with DatabaseManager.get_connection() as conn:
                result = conn.execute("SELECT * FROM table")
        """
        conn = None
        try:
            conn = get_conn()
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def handle_database_errors(func: Callable) -> Callable:
        """
        Decorator per gestire automaticamente gli errori del database.
        
        Usage:
            @DatabaseManager.handle_database_errors
            def my_function():
                with DatabaseManager.get_connection() as conn:
                    return conn.execute("SELECT * FROM table").fetchall()
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except sqlite3.Error as e:
                logger.error(f"Database operation failed in {func.__name__}: {e}")
                raise
        return wrapper
    
    @staticmethod
    def execute_query(query: str, params: tuple = ()) -> list:
        """
        Esegue una query e restituisce i risultati.
        
        Args:
            query: Query SQL da eseguire
            params: Parametri della query (per sicurezza)
            
        Returns:
            Lista di righe risultanti
        """
        with DatabaseManager.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    @staticmethod
    def execute_update(query: str, params: tuple = ()) -> int:
        """
        Esegue una query di update/insert/delete.
        
        Args:
            query: Query SQL da eseguire
            params: Parametri della query
            
        Returns:
            ID dell'ultimo record inserito (se INSERT) o numero righe affected
        """
        with DatabaseManager.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid or cursor.rowcount
