
New/
├── core/                    # Componenti core del sistema
│   └── database.py          # DatabaseManager centralizzato
├── routes/                  # Rotte API e UI
│   ├── api/                 # Endpoints REST API
│   │   ├── analytics.py     # Statistiche e analytics
│   │   ├── ingredienti.py   # Gestione ingredienti
│   │   ├── ingredienti_new.py # Variante API ingredienti
│   │   ├── menu.py          # Gestione menu pizze
│   │   ├── order_modifications.py # Modifiche ordini
│   │   └── orders.py        # Gestione ordini
│   └── ui/                  # Pagine HTML/interfacce
│       ├── analytics.py     # Pagina statistiche
│       ├── ingredienti_management.py # Gestione ingredienti UI
│       ├── management.py    # Dashboard management
│       └── orders.py        # Gestione ordini UI
├── services/                # Servizi esterni
│   └── print_service.py     # Stampa scontrini
├── templates/               # Template HTML
│   ├── analytics.html       # Pagina analytics
│   ├── base.html            # Template base
│   ├── ingredienti_management.html # Gestione ingredienti
│   ├── management.html      # Dashboard
│   └── orders.html          # Gestione ordini
├── static/                  # Asset frontend
│   ├── css/
│   └── js/
├── tests/                   # Test ufficiali
│   └── test_api.py          # Test API
├── tests_archive/           # Test e script storici
├── main.py                  # Entry point FastAPI
├── models.py                # Data classes per dominio
├── schemas.py               # Pydantic schemas
├── test_api_ingredienti.py  # Test API ingredienti
├── test_api_ingredienti_minimal.py
├── test_requirements.txt    # Dipendenze di test
├── verify_structure.py      # Verifica struttura progetto
└── pizzeria.db              # Database SQLite

Stili di Programmazione Utilizzati

1. **DataClasses** (models.py)
```python
@dataclass
class Ingrediente:
    id: int = field(default=None)
    nome: str = field(default=None)
    tipo: str = 'altro'

    @classmethod
    def from_db(cls, row: sqlite3.Row) -> 'Ingrediente':
        """Crea oggetto da riga database"""
```
---

### 2. **Pydantic Schemas** (schemas.py)
```python
class IngredienteCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    tipo: str = Field(default='altro')
    costo_unitario: float = Field(default=0.0, ge=0)
    unita_riferimento: str = Field(default='pz')
    quantita_riferimento: float = Field(default=1.0, gt=0)
```

### 3. **Router Pattern** (routes/api/*.py)
```python
router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/")
def create_order(order_data: dict):
    # Logica business
```

### 4. **Context Manager Pattern** (core/database.py)
```python
class DatabaseManager:
    @staticmethod
    @contextmanager
    def get_connection() -> Generator[sqlite3.Connection, None, None]:
        try:
            conn = get_conn()
            yield conn
        finally:
            conn.close()
```

### 5. **Vanilla JavaScript** (templates/*.html)
```javascript
// Global state management
let tablesOrders = {};
let selectedTable = null;

// Async/await pattern
async function loadMenu() {
    try {
        const response = await fetch('/menu');
        const menu = await response.json();
        renderMenu(menu);
    } catch (error) {
        console.error('Error loading menu:', error);
    }
}
```

Pattern Architetturali

### 1. **MVC-like Structure**
Models (DataClasses) ↔ API Routes (Controllers) ↔ Templates (Views)

### 2. **Repository Pattern**
```python
@classmethod
def get_all(cls) -> List['Ingrediente']:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM ingredienti WHERE attiva = 1 ORDER BY nome").fetchall()
    return [cls.from_db(row) for row in rows]
```

### 3. **Service Layer Pattern**
```python
class PrintService:
    def print_order(self, order_data: dict) -> bool:
        # Logica di stampa
```

### 4. **Factory Pattern**
```python
@classmethod
def from_db(cls, row: sqlite3.Row) -> 'Ingrediente':
    return cls(**dict(row))
```

Flusso Dati Tipico
1. **Request** → FastAPI Router
2. **Validation** → Pydantic Schema
3. **Business Logic** → Router Function
4. **Data Access** → DatabaseManager
5. **Model Creation** → DataClass from_db()
6. **Response** → JSON serialization

Frontend Architecture

**Component-based UI**
- HTML templates con Jinja2
- JavaScript vanilla per interattività
- CSS e asset statici per styling

**State Management**
```javascript
let tablesOrders = {};
let selectedTable = null;
let currentOrderId = null;
let ingredientsData = {};
let currentEditingItemId = null;
```

**Event-driven Updates**
- Event listeners su input/select
- Async fetch per dati backend
- DOM manipulation per UI updates

---

## Principi SOLID Applicati

### Single Responsibility
- Ogni router ha una responsabilità specifica
- DataClasses solo per dati
- Services solo per logica esterna

### Open/Closed
- Router possono essere estesi senza modificare core
- Nuovi endpoint senza toccare esistenti

### Liskov Substitution
- DataClasses possono essere sostituite
- DatabaseManager interface consistente

### Interface Segregation
- API routes separate da UI routes
- Schemas specifici per ogni use case

### Dependency Inversion
- FastAPI inietta dependencies
- DatabaseManager astrae connection details

## Best Practices Implementate

### 1. Error Handling
```python
try:
    result = conn.execute(query)
except sqlite3.Error as e:
    raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

### 2. Type Safety
```python
def create_order(order_data: dict) -> dict:
    # Type hints per chiarezza
```

### 3. Resource Management
```python
with DatabaseManager.get_connection() as conn:
    # Connection automaticamente chiusa
```

### 4. Validation
```python
class IngredienteCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    costo_unitario: float = Field(ge=0)
```

---

## Modelli Dati Principali

### Ingrediente (DataClass)
- **Purpose**: Rappresenta ingrediente singolo
- **Fields**: id, nome, tipo, costo_unitario, unita_riferimento, quantita_riferimento, attiva
- **Methods**: from_db(), get_all(), create(), to_dict()

### MenuItem (DataClass)
- **Purpose**: Rappresenta voce di menu con ingredienti
- **Fields**: id, nome, prezzo, categoria, ingredienti
- **Methods**: from_db(), get_all(), create(), to_dict()

### Ordine (Database-driven)
- **Purpose**: Rappresenta ordine cliente
- **Storage**: Database SQLite
- **Relations**: ordine_dettagli → menu_items

Note di Sviluppo

- **Database**: SQLite con schema gestito in `core/database.py`
- **Frontend**: Jinja2 templates e JavaScript vanilla
- **API**: RESTful con FastAPI
- **Testing**: pytest e test suite in `tests/` e `tests_archive/`
- **Deployment**: Single process FastAPI app

