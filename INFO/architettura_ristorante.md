# ARCHITETTURA SISTEMA GESTIONE RISTORANTE

## 1. DESCRIZIONE ARCHITETTURA

### Architettura a 3 Livelli
**Frontend (Presentation Layer)**
- Interfaccia web basata su browser
- Template HTML dinamici con Jinja2
- JavaScript vanilla per interattività
- Layout ottimizzato per desktop/tablet

**Backend (Business Logic Layer)**
- API REST con FastAPI
- Validazione input lato server in Python
- Gestione ordini, menu, ingredienti e analytics
- Servizi ausiliari come stampa scontrini in `services/print_service.py`

**Database (Data Layer)**
- Database SQLite per semplicità e manutenzione
- Schema definito in `core/database.py`
- Soft delete per ingredienti e menu item
- Accesso centralizzato con `DatabaseManager`

### Flusso Dati Principale
```
Browser UI → HTTP Request → FastAPI Backend → Database SQLite
                ← Response JSON ← Business Logic ← Query Results
```

## 2. STRUTTURA CARTELLE PROGETTO

```
New/
├── core/
│   └── database.py
├── routes/
│   ├── api/
│   │   ├── analytics.py
│   │   ├── ingredienti.py
│   │   ├── ingredienti_new.py
│   │   ├── menu.py
│   │   ├── order_modifications.py
│   │   └── orders.py
│   └── ui/
│       ├── analytics.py
│       ├── ingredienti_management.py
│       ├── management.py
│       └── orders.py
├── services/
│   └── print_service.py
├── templates/
│   ├── analytics.html
│   ├── base.html
│   ├── ingredienti_management.html
│   ├── management.html
│   └── orders.html
├── static/
│   ├── css/
│   └── js/
├── tests/
│   └── test_api.py
├── tests_archive/
├── main.py
├── models.py
├── schemas.py
├── test_api_ingredienti.py
├── test_api_ingredienti_minimal.py
├── test_requirements.txt
├── verify_structure.py
└── pizzeria.db
```

## 3. SCHEMA DATABASE PRINCIPALE

### Tabella Ingredienti
```sql
CREATE TABLE IF NOT EXISTS ingredienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    tipo TEXT DEFAULT 'altro' CHECK(tipo IN ('base', 'salsa', 'formaggio', 'carne', 'verdura', 'premade', 'altro')),
    costo_unitario REAL NOT NULL CHECK(costo_unitario >= 0),
    unita_riferimento TEXT DEFAULT 'pz' CHECK(unita_riferimento IN ('g', 'ml', 'pz', 'kg', 'l')),
    quantita_riferimento REAL NOT NULL DEFAULT 1 CHECK(quantita_riferimento > 0),
    attiva INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))
);
```

### Tabella Menu Items
```sql
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    prezzo REAL NOT NULL CHECK(prezzo >= 0),
    categoria TEXT DEFAULT 'Pizza',
    attiva INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))
);
```

### Tabella Relazione menu-ingredienti
```sql
CREATE TABLE IF NOT EXISTS menu_item_ingredienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_item_id INTEGER NOT NULL,
    ingrediente_id INTEGER NOT NULL,
    quantita REAL NOT NULL CHECK(quantita > 0),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredienti(id) ON DELETE CASCADE,
    UNIQUE(menu_item_id, ingrediente_id)
);
```

### Tabella Ordini
```sql
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
);
```

### Tabella Dettagli Ordine
```sql
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
);
```

## 4. DESCRIZIONE MODULI PRINCIPALI

### Modulo Gestione Menu
**Responsabilità:**
- CRUD ingredienti
- CRUD menu item
- Associazione ingredienti per menu item
- Soft delete per menu item e ingredienti

**API principali:**
- `/ingredienti`
- `/menu`

### Modulo Presa Ordini
**Responsabilità:**
- Creazione ordini
- Unione ordini esistenti per tavolo
- Gestione item con prezzo personalizzato
- Stampa scontrini opzionale

**API principali:**
- `/orders`
- `/api/v1/orders/...` (order modifications)

### Modulo Analytics
**Responsabilità:**
- Metriche ricavi
- Trend ordini
- Performance prodotti

**API principali:**
- `/analytics/summary`
- `/analytics/trends`

### Modulo UI Frontend
**Responsabilità:**
- Pagina management per menu
- Pagina gestione ingredienti
- Pagina presa ordini
- Dashboard analytics

**Template principali:**
- `management.html`
- `ingredienti_management.html`
- `orders.html`
- `analytics.html`

## 5. FLUSSO DATI SISTEMA

### Flusso Ordine Tipico
1. **UI**: Cameriere seleziona tavolo e prodotti
2. **API**: POST `/orders` con dati ordine
3. **Server**: Validazione e calcolo totali
4. **Database**: Inserimento ordine e dettagli
5. **Response**: Conferma ordine
6. **UI**: Aggiornamento stato e conferma

### Flusso Analytics
1. **UI**: Richiesta metriche periodo specifico
2. **API**: GET `/api/analytics/ricavi?period=giorno`
3. **Service**: Query database con filtri temporali
4. **Database**: Calcoli aggregati su ordini
5. **Response**: JSON con dati statistici
6. **UI**: Visualizzazione grafici e tabelle

### Flusso Gestione Menu
1. **UI**: Form creazione/modifica prodotto
2. **API**: POST/PUT `/api/menu` con dati prodotto
3. **Service**: Validazione prezzi e ingredienti
4. **Database**: Aggiornamento tabelle menu e composizione
5. **Response**: Conferma aggiornamento
6. **UI**: Refresh elenco prodotti aggiornato
