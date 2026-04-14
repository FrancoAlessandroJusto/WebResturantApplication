# =========================

# IMPORT DI BASE

# =========================



import os          # Gestione dei percorsi del filesystem (cartelle, path assoluti)

import sqlite3     # Database SQLite integrato in Python





# =========================

# CONFIGURAZIONE PERCORSI

# =========================



# Percorso della cartella in cui si trova questo file (db.py)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



# Percorso completo del file database SQLite

DB_PATH = os.path.join(BASE_DIR, "pizzeria.db")





# =========================

# CONNESSIONE AL DATABASE

# =========================



def get_conn() -> sqlite3.Connection:

    """

    Crea e restituisce una connessione al database SQLite.

    Viene usata da tutte le query dell'applicazione.

    """



    # check_same_thread=False:

    # permette l'uso della connessione in un contesto web multithread (FastAPI + uvicorn)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10.0)



    # row_factory:

    # consente di accedere alle colonne per nome (row["nome"])

    # invece che per indice numerico (row[1])

    conn.row_factory = sqlite3.Row



    return conn





# =========================

# INIZIALIZZAZIONE DATABASE

# =========================



def init_db() -> None:

    """

    Inizializza lo schema del database.

    Crea le tabelle solo se non esistono già.

    """



    # Apre una connessione al database

    conn = get_conn()



    # Il cursore è l'oggetto che esegue i comandi SQL

    cur = conn.cursor()



    # CREATE TABLE IF NOT EXISTS:

    # - definisce lo schema fisso

    # - non sovrascrive dati esistenti

    cur.execute("""

    CREATE TABLE IF NOT EXISTS ingredienti (
        
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        
        nome    TEXT NOT NULL UNIQUE,
        
        tipo TEXT DEFAULT 'altro' CHECK(tipo IN ('base', 'salsa', 'formaggio', 'carne', 'verdura', 'premade', 'altro')),
        
        costo_unitario REAL NOT NULL CHECK(costo_unitario >= 0),
        
        unita_riferimento TEXT DEFAULT 'pz' CHECK(unita_riferimento IN ('g', 'ml', 'pz', 'kg', 'l')),
        
        quantita_riferimento REAL NOT NULL DEFAULT 1 CHECK(quantita_riferimento > 0),
        
        attiva  INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))

    )

    """)



    # Migrazioni per aggiungere nuovi campi se mancanti

    try:

        cur.execute("ALTER TABLE ingredienti ADD COLUMN quantita_riferimento REAL NOT NULL DEFAULT 1 CHECK(quantita_riferimento > 0)")

        conn.commit()

    except sqlite3.OperationalError:

        # Il campo esiste già, ignora l'errore

        pass



    # Tabella menu_items (articoli del menu: pizze, bevande, etc.)

    cur.execute("""

    CREATE TABLE IF NOT EXISTS menu_items (
        
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        
        nome        TEXT NOT NULL UNIQUE,
        
        prezzo      REAL NOT NULL CHECK(prezzo >= 0),
        
        categoria   TEXT DEFAULT 'Pizza',
        
        attiva      INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))
        
    )
    
    """)

    # Tabella di collegamento tra menu_items e ingredienti
    cur.execute("""

    CREATE TABLE IF NOT EXISTS menu_item_ingredienti (
        
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        
        menu_item_id    INTEGER NOT NULL,
        
        ingrediente_id  INTEGER NOT NULL,
        
        quantita        REAL NOT NULL CHECK(quantita > 0),
        
        FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
        
        FOREIGN KEY (ingrediente_id) REFERENCES ingredienti(id) ON DELETE CASCADE,
        
        UNIQUE(menu_item_id, ingrediente_id)

    )

    """)

    # Migrate old pizzas only if menu_items is empty and pizze table exists and has data
    cur.execute("SELECT COUNT(*) as count FROM menu_items")
    menu_count = cur.fetchone()["count"]
    
    # Check if pizze table exists and has data
    pizzas_exist = False
    try:
        cur.execute("SELECT COUNT(*) as count FROM pizze WHERE attiva = 1")
        pizzas_count = cur.fetchone()["count"]
        pizzas_exist = pizzas_count > 0
    except sqlite3.OperationalError:
        # pizze table doesn't exist
        pizzas_exist = False
    
    if menu_count == 0 and pizzas_exist:
        cur.execute("""
        INSERT INTO menu_items (nome, prezzo, categoria, attiva)
        SELECT nome, prezzo, 'Pizza', attiva FROM pizze WHERE attiva = 1
        """)
        
        # After migration, disable the old pizzas table
        cur.execute("UPDATE pizze SET attiva = 0 WHERE 1=1")





    # Rende permanenti le modifiche allo schema

    conn.commit()



    # Chiude la connessione al database

    conn.close()

