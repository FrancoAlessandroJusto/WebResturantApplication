# PROMPT DI TEST PER SISTEMA GESTIONE RISTORANTE - PIZZAADMIN

## TASK:
Creare test completi per il sistema di gestione ristorante esistente, verificando tutte le funzionalità principali e i componenti tecnici implementati.

## CONTESTO TECNICO SPECIFICO:
Il progetto esistente utilizza:
- **Backend**: FastAPI con Python
- **Database**: SQLite con schema relazionale
- **Frontend**: HTML templates con TailwindCSS e JavaScript vanilla
- **Architettura**: MVC con separazione chiara tra modelli, rotte e template

## STRUTTURA PROGETTO ESISTENTE:
```
Nap2.0/New/
├── main.py                    # Entry point FastAPI
├── models.py                  # Data class per entità (Ingrediente, MenuItem)
├── schemas.py                 # Pydantic schemas
├── core/
│   └── database.py           # Gestione database SQLite
├── routes/
│   ├── api/                  # API REST endpoints
│   │   ├── menu.py
│   │   ├── ingredienti.py
│   │   ├── orders.py
│   │   ├── analytics.py
│   │   └── order_modifications.py
│   └── ui/                   # Template rendering routes
│       ├── management.py
│       ├── ingredienti_management.py
│       ├── orders.py
│       └── analytics.py
├── services/                 # Business logic
├── templates/               # HTML templates
│   ├── base.html
│   ├── management.html
│   ├── ingredienti_management.html
│   ├── orders.html
│   └── analytics.html
├── static/                  # CSS, JS, assets
├── tests/                   # Test directory
└── pizzeria.db             # Database SQLite
```

## SCHEMA DATABASE ESISTENTE:
```sql
-- Ingredienti
CREATE TABLE ingredienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    tipo TEXT DEFAULT 'altro' CHECK(tipo IN ('base', 'salsa', 'formaggio', 'carne', 'verdura', 'premade', 'altro')),
    costo_unitario REAL NOT NULL CHECK(costo_unitario >= 0),
    unita_riferimento TEXT DEFAULT 'pz' CHECK(unita_riferimento IN ('g', 'ml', 'pz', 'kg', 'l')),
    quantita_riferimento REAL NOT NULL DEFAULT 1 CHECK(quantita_riferimento > 0),
    attiva INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))
);

-- Menu items
CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    prezzo REAL NOT NULL CHECK(prezzo >= 0),
    categoria TEXT DEFAULT 'Pizza',
    attiva INTEGER NOT NULL DEFAULT 1 CHECK(attiva IN (0,1))
);

-- Relazione menu-ingredienti
CREATE TABLE menu_item_ingredienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_item_id INTEGER NOT NULL,
    ingrediente_id INTEGER NOT NULL,
    quantita REAL NOT NULL CHECK(quantita > 0),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredienti(id) ON DELETE CASCADE,
    UNIQUE(menu_item_id, ingrediente_id)
);

-- Ordini
CREATE TABLE ordini (
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

-- Dettagli ordini
CREATE TABLE ordine_dettagli (
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

## COMPONENTI PRINCIPALI DA TESTARE:

### 1. MODELLI (models.py)
- **Ingrediente class**: 
  - Metodi: from_db(), get_all(), create(), to_dict()
  - Validazione costi e unità di misura
  - Soft delete con flag attiva

- **MenuItem class**:
  - Metodi: from_db(), get_all(), create(), to_dict(), get_ingredienti_string()
  - Calcolo automatico costo ingredienti
  - Gestione relazioni molti-a-molti con ingredienti

- **IngredienteQuantita class**:
  - Conversione costi unitari reali
  - Formattazione dizionari per template

### 2. DATABASE MANAGER (core/database.py)
- **DatabaseManager class**:
  - Context manager per connessioni sicure
  - Decorator per error handling
  - Metodi execute_query() e execute_update()
  - Inizializzazione schema con init_db()

### 3. API ENDPOINTS (routes/api/)
- **menu.py**: CRUD operazioni su menu items
- **ingredienti.py**: CRUD operazioni su ingredienti
- **orders.py**: Gestione ordini e dettagli
- **analytics.py**: Metriche e statistiche
- **order_modifications.py**: Modifiche ordini esistenti

### 4. UI ROUTES (routes/ui/)
- Rendering template con dati dinamici
- Gestione form HTML
- Integrazione con backend API

### 5. TEMPLATES (templates/)
- **base.html**: Layout principale con TailwindCSS
- **management.html**: Gestione completa ristorante
- **ingredienti_management.html**: Gestione ingredienti
- **orders.html**: Interfaccia presa ordini
- **analytics.html**: Dashboard analitiche

## REQUISITI DI TEST SPECIFICI:

### A. UNIT TEST
1. **Test Modelli**:
   - Creazione ingredienti con validazione costi/unità
   - Creazione menu items con calcolo automatico costi
   - Relazioni molti-a-molti corrette
   - Soft delete functionality

2. **Test Database**:
   - Connessioni sicure con context manager
   - Transazioni rollback su errori
   - Validazione constraints SQL
   - Performance query comuni

3. **Test API**:
   - CRUD operations complete
   - Validazione input con Pydantic
   - Error handling HTTP status codes
   - Response format consistency

### B. INTEGRATION TEST
1. **Flusso Ordine Completo**:
   - Creazione ingredienti → menu items → ordine → pagamento
   - Calcolo automatico totali e costi
   - Aggiornamento stato ordine

2. **Modifiche Ordini**:
   - Aggiunta/rimozione items
   - Ricalcolo automatico prezzi
   - Tracking modifiche

3. **Analytics Integration**:
   - Calcolo ricavo medio per coperto
   - Statistiche vendite per prodotto
   - Andamento temporale ricavi

### C. UI/E2E TEST
1. **Interfaccia Management**:
   - Form gestione ingredienti
   - Form gestione menu
   - Validazione frontend

2. **Interfaccia Ordini**:
   - Selezione prodotti da menu
   - Calcolo automatico totale
   - Gestione tavoli

3. **Dashboard Analytics**:
   - Visualizzazione metriche
   - Filtri temporali
   - Export dati

## CRITERI DI SUCCESSO:

### Funzionalità
- ✅ CRUD completo per tutte le entità
- ✅ Calcoli automatici costi/prezzi
- ✅ Gestione stati ordini
- ✅ Analytics accurate
- ✅ UI responsive e funzionante

### Performance
- ✅ Tempo risposta API < 200ms
- ✅ Rendering template < 100ms
- ✅ Query database ottimizzate
- ✅ Gestione concorrente multi-utente

### Robustezza
- ✅ Validazione input completa
- ✅ Error handling graceful
- ✅ Database consistency
- ✅ UI error states

### Security
- ✅ SQL injection prevention
- ✅ Input sanitization
- ✅ Data validation
- ✅ Error message sanitization

## STRUMENTI DI TEST:
- **Unit**: pytest + unittest.mock
- **Integration**: pytest + test database SQLite
- **API**: pytest + httpx (FastAPI TestClient)
- **UI**: pytest + playwright/selenium
- **Database**: pytest + fixtures per setup/teardown

## OUTPUT ATTESO:
1. Suite completa test unità (>90% coverage)
2. Test integrazione flussi principali
3. Test E2E interfacce critiche
4. Performance benchmark
5. Documentazione test cases
6. CI/CD pipeline configuration

## VINCOLI SPECIFICI:
- Mantenere compatibilità con schema database esistente
- Non modificare API contracts esistenti
- Testare con dati realistici (pizzeria)
- Validare calcoli economici precisione monetaria
- Testare responsive design mobile/desktop
