Sistema completo per la gestione di ristoranti/pizzerie con tre modalità operative dedicate: 
Taking Order 
Management 
Analytics (work in progress)

L'applicazione permette gestione dinamica di menù, ingredienti e ordini direttamente dal database durante l'esecuzione

## Requisiti e Setup

### Installazione Dipendenze
 # Pizzeria Napoletana 2.0 — Management System

Breve sistema per gestire il menù, gli ingredienti e gli ordini in una pizzeria.
Questa repository contiene una piccola applicazione FastAPI con interfacce HTML (Jinja2)
per Management, Taking Orders e una dashboard Analytics di base.


## Quick Start (locale)

Prerequisiti: Python 3.10+ (consigliato) e pip.
Avvia l'app in sviluppo:

```bash
python -m uvicorn main:app --reload --port 8000
```
Pagine principali:
- Management UI: http://127.0.0.1:8000/mgmt/ui
- Orders UI: http://127.0.0.1:8000/orders/ui
- Analytics UI: http://127.0.0.1:8000/analytics/ui
- API docs (Swagger): http://127.0.0.1:8000/docs

---

## Esempi API (curl)

Lista ingredienti:

```bash
curl -s http://127.0.0.1:8000/ingredienti | jq
```

Creazione ingrediente (POST):

```bash
curl -X POST http://127.0.0.1:8000/ingredienti \
  -H 'Content-Type: application/json' \
  -d '{"nome":"Mozzarella","tipo":"formaggio","costo_unitario":4.5,"unita_riferimento":"kg","quantita_riferimento":1}'
```

Aggiorna ingrediente (PUT):

```bash
curl -X PUT http://127.0.0.1:8000/ingredienti/3 \
  -H 'Content-Type: application/json' \
  -d '{"costo_unitario":5.0}'
```

---

## Database

- Percorso di riferimento: `New/core/database.py` definisce il percorso assoluto del DB:
  - `BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`
  - `DB_PATH = os.path.join(BASE_DIR, 'pizzeria.db')`
-  `get_conn()` o `DatabaseManager.get_connection()` per aprire connessioni.
- Alcuni script  in `tests/tests_archive` potrebbero usare percorsi relativi

---

## Eseguire i test

Per eseguire tutta la suite:

```bash
python -m pytest -q
```

Per eseguire un singolo file o test:

```bash
python -m pytest New/tests/test_api_ingredienti.py -q
python -m pytest New/tests/test_api_ingredienti.py::test_create_ingrediente_success -q
```

Se i test falliscono, verifica lo stato del database oppure esegui `init_db()` per ripristinarlo.

---

## Struttura essenziale del progetto

- `main.py` — entry FastAPI
- `core/database.py` — gestione centralizzata del DB (`get_conn`, `init_db`, `DatabaseManager`)
- `routes/api/` — endpoint REST (ingredienti, menu, ordini, analytics)
- `routes/ui/` — pagine HTML (management, orders, analytics)
- `services/print_service.py` — logica di stampa / statistiche
- `models.py` / `schemas.py` — modelli dati e validazione

Per dettagli architetturali rimando a `INFO/CODE_STRUCTURE.md`.

---

## Roadmap del progetto

Questa sezione descrive a colpo d'occhio cosa contiene ogni cartella principale e i file più importanti.

- `main.py`
  - Entry-point dell'app FastAPI.
  - Include i router UI e API e chiama `init_db()` all'avvio.

- `core/`
  - `database.py`: configurazione del database SQLite e funzioni condivise.
  - Definisce `BASE_DIR`, `DB_PATH`, `get_conn()`, `init_db()` e `DatabaseManager`.

- `routes/api/`
  - Contiene gli endpoint REST per le entità di business.
  - `ingredienti.py`: CRUD ingredienti e validazione input/output.
  - `menu.py`: gestione dei menu items e relazione ingredienti-pizza.
  - `orders.py`: gestione ordini e logica checkout.
  - `analytics.py`: endpoint per statistiche e report.
  - `order_modifications.py`: operazioni extra su ordini esistenti.

- `routes/ui/`
  - Costruisce le pagine HTML per l'interfaccia utente.
  - `management.py`: dashboard per la gestione del menù.
  - `ingredienti_management.py`: gestione ingredienti via web.
  - `orders.py`: pagina di presa ordini per il personale.
  - `analytics.py`: dashboard analytics base.

- `services/`
  - `print_service.py`: funzioni per preparare e salvare i dati di stampa.
  - Gestisce anche statistiche sugli ordini in un DB di supporto.

- `models.py`
  - Definisce le classi dati principali (`Ingrediente`, `IngredienteQuantita`, `MenuItem`).
  - Implementa metodi `from_db()`, `get_all()`, `create()` e serializzazione.

- `schemas.py`
  - Contiene i modelli Pydantic usati per validazione e serializzazione API.
  - Dichiara gli schemi `IngredienteCreate`, `IngredienteUpdate`, `IngredienteOut`, `MenuItemCreate`, `MenuItemUpdate`, `MenuItemOut`.

- `templates/`
  - Modelli Jinja2 per le pagine UI.
  - `base.html`: layout comune.
  - `management.html`, `orders.html`, `ingredienti_management.html`, `analytics.html`.

- `static/`
  - Risorse client statiche (CSS, JS).

- `tests/`
  - Test automatici per API e funzionalità principali.
  - `test_api_ingredienti.py`: verifica comportamento CRUD ingredienti.
  - `test_api.py`: test API generali.
  - `test_analytics.py`: verifiche su reporting/analytics.
  - `tests_archive/`: script e test legacy o di supporto.

- `INFO/`
  - Documentazione di progetto, roadmap e note tecniche.
  - Contiene mappe del codice, architettura e known issues.

---

### Nota sul Database
- L'app utilizza un percorso assoluto per il database definito in `core/database.py`:
    - `BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`
    - `DB_PATH = os.path.join(BASE_DIR, 'pizzeria.db')`
- Tutte le chiamate al DB dovrebbero usare `get_conn()` o `DatabaseManager.get_connection()` per garantire coerenza del percorso.
- Alcuni script di utilità/archivio possono ancora usare percorsi relativi: presta attenzione quando li esegui.


##  Sviluppi Futuri

1. **Gestione Avanzata Magazzino**
   - Tracking movimenti ingredienti
   - Previsioni stock automatiche
   - Ordini automatici fornitori

2. **Sistema Autenticazione Utenti**
   - Login multi-ruolo (cameriere, manager, owner)
   - Password hashing e JWT tokens
   - Audit log per operazioni critiche

3. **Stampa Comande Cucina**
   - Integrazione stampante Bluetooth
   - Formato scontrino personalizzabile
   - Coda ordini in tempo reale

4. **Reportistica Avanzata**
   - Export PDF/Excel
   - Grafici dashboard interattivi
   - Scheduling report automatici

5. **Integrazione Pagamenti Elettronici**
   - Stripe/Square integration
   - Split bill support
   - Gestione promozionali e sconti

6. **Mobile App**
   - App camerieri per ordini
   - App owner per analytics real-time
   - Push notifications

---

## 📚 Tecnologie Utilizzate

| Componente | Tecnologia |
|------------|------------|
| Backend    | FastAPI 0.135.1 |
| Server     | Uvicorn |
| Database   | SQLite3 |
| Frontend   | HTML5 + Jinja2 |
| Styling    | TailwindCSS 3 |
| Interattività | JavaScript Vanilla |
| Validazione   | Pydantic 2.12.5 |
| Testing       | pytest + httpx |
| Python        | 3.14.3 |

---

## 💡 Note di Sviluppo

- **Database**: SQLite con schema gestito in `core/database.py`
- **Frontend**: Jinja2 templates e JavaScript vanilla (zero framework)
- **API**: RESTful completa con validazione Pydantic
- **Testing**: pytest con TestClient di Starlette
- **Deployment**: Single process FastAPI app (upgrade con gunicorn per production)
- **Services**: Moduli di servizio in `services/` (es. print_service.py per stampa)
- **Static Assets**: CSS e JavaScript in `static/` directory

---

##  Support e Debug

### Check Struttura Progetto
```bash
python verify_structure.py
```

### Log Server Dettagliati
```bash
python -m uvicorn main:app --reload --port 8000 --log-level debug
```
