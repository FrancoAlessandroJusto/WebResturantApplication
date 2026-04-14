# ARCHITETTURA SISTEMA GESTIONE RISTORANTE

## 1. DESCRIZIONE ARCHITETTURA

### Architettura a 3 Livelli
**Frontend (Presentation Layer)**
- Interfaccia web responsive basata su browser
- Template HTML dinamici con CSS framework moderno
- JavaScript vanilla per interattività client-side
- Design mobile-first per tablet e smartphone

**Backend (Business Logic Layer)**
- API REST con framework Python (FastAPI/Flask)
- Validazione input e business rules
- Gestione stato ordini e calcoli economici
- Autenticazione base per staff ristorante

**Database (Data Layer)**
- Database SQLite per semplicità e manutenzione
- Schema relazionale con integrità referenziale
- Backup automatico dei dati
- Query ottimizzate per analisi in tempo reale

### Flusso Dati Principale
```
Browser UI → HTTP Request → API Backend → Database SQLite
                ← Response JSON ← Business Logic ← Query Results
```

## 2. STRUTTURA CARTELLE PROGETTO

```
ristorante-app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point applicazione
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── ingredienti.py
│   │   ├── menu.py
│   │   ├── ordini.py
│   │   └── analytics.py
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── menu.py
│   │   ├── ordini.py
│   │   ├── tavoli.py
│   │   └── analytics.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── ordini_service.py
│   │   ├── menu_service.py
│   │   └── analytics_service.py
│   ├── database/               # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── migrations/
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── validators.py
├── static/                     # Assets frontend
│   ├── css/
│   ├── js/
│   └── images/
├── templates/                  # HTML templates
│   ├── base.html
│   ├── ordini/
│   ├── menu/
│   ├── tavoli/
│   └── analytics/
├── tests/                      # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                       # Documentazione
├── requirements.txt            # Dipendenze Python
├── config.py                   # Configurazione
└── run.py                      # Script avvio
```

## 3. SCHEMA DATABASE PRINCIPALE

### Tabella Ingredienti
```sql
CREATE TABLE ingredienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    tipo TEXT DEFAULT 'altro',
    costo_unitario REAL NOT NULL,
    unita_riferimento TEXT DEFAULT 'pz',
    quantita_riferimento REAL DEFAULT 1,
    attiva BOOLEAN DEFAULT TRUE
);
```

### Tabella Menu Items
```sql
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    prezzo REAL NOT NULL,
    categoria TEXT DEFAULT 'Pizza',
    attiva BOOLEAN DEFAULT TRUE
);
```

### Tabella Composizione Menu
```sql
CREATE TABLE menu_composizione (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_item_id INTEGER,
    ingrediente_id INTEGER,
    quantita REAL NOT NULL,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id),
    FOREIGN KEY (ingrediente_id) REFERENCES ingredienti(id)
);
```

### Tabella Tavoli
```sql
CREATE TABLE tavoli (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER UNIQUE NOT NULL,
    posti INTEGER NOT NULL,
    stato TEXT DEFAULT 'libero'
);
```

### Tabella Ordini
```sql
CREATE TABLE ordini (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tavolo_id INTEGER,
    data_ora DATETIME DEFAULT CURRENT_TIMESTAMP,
    stato TEXT DEFAULT 'aperto',
    totale REAL DEFAULT 0,
    numero_persone INTEGER DEFAULT 1,
    coperto REAL DEFAULT 0,
    FOREIGN KEY (tavolo_id) REFERENCES tavoli(id)
);
```

### Tabella Dettagli Ordine
```sql
CREATE TABLE ordine_dettagli (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ordine_id INTEGER,
    menu_item_id INTEGER,
    quantita INTEGER NOT NULL,
    prezzo_unitario REAL NOT NULL,
    note TEXT,
    FOREIGN KEY (ordine_id) REFERENCES ordini(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);
```

## 4. DESCRIZIONE MODULI PRINCIPALI

### Modulo Gestione Menu
**Responsabilità:**
- CRUD ingredienti con costi e unità misura
- CRUD piatti del menu con prezzi
- Calcolo automatico costo ingredienti per piatto
- Categorizzazione prodotti (pizze, bevande, antipasti)

**API principali:**
- GET/POST/PUT/DELETE `/api/ingredienti`
- GET/POST/PUT/DELETE `/api/menu`
- GET `/api/menu/categorie`
- POST `/api/menu/calcola-costo`

### Modulo Presa Ordini
**Responsabilità:**
- Gestione stati tavoli (libero/occupato)
- Creazione e modifica ordini
- Calcolo automatico totali e coperti
- Tracking stato preparazione/servizio

**API principali:**
- GET/POST `/api/tavoli`
- POST `/api/ordini`
- PUT `/api/ordini/{id}/stato`
- POST `/api/ordini/{id}/dettagli`

### Modulo Analytics
**Responsabilità:**
- Calcolo ricavo medio per coperto
- Statistiche vendite per periodo
- Analisi prodotti più venduti
- Report performance economica

**API principali:**
- GET `/api/analytics/ricavi`
- GET `/api/analytics/prodotti-venduti`
- GET `/api/analytics/clienti-per-periodo`
- GET `/api/analytics/ricavo-medio-coperto`

### Modulo UI Frontend
**Responsabilità:**
- Interfaccia responsive per tablet/phone
- Form validati per inserimento dati
- Dashboard analytics in tempo reale
- Gestione stati loading/error

**Template principali:**
- `ordini/nuovo-ordine.html`
- `menu/gestione-menu.html`
- `tavoli/stato-tavoli.html`
- `analytics/dashboard.html`

## 5. FLUSSO DATI SISTEMA

### Flusso Ordine Tipico
1. **UI**: Cameriere seleziona tavolo e prodotti
2. **API**: POST `/api/ordini` con dati ordine
3. **Service**: Validazione e calcolo totali
4. **Database**: Inserimento ordine e dettagli
5. **Response**: Conferma con ID ordine e totale
6. **UI**: Aggiornamento stato tavolo e dashboard

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
