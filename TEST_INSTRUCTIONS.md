# =========================
# ISTRUZIONI ESECUZIONE TEST
# =========================

# 📋 REQUISITI PER ESEGUIRE I TEST

## Dipendenze necessarie
```bash
pip install fastapi uvicorn pytest
pip install python-multipart jinja2
```

## 🚀 COME ESEGUIRE I TEST

### 1. Verifica Strutturale
```bash
# Verifica che la struttura del progetto sia corretta
python verify_structure.py
```

### 2. Test Completi API
```bash
# Esegui tutti i test automatici
python test_api_ingredienti.py

# Oppure con pytest per output dettagliato
pytest test_api_ingredienti.py -v

# Con traceback completo
pytest test_api_ingredienti.py -v --tb=short

# Solo test specifici
pytest test_api_ingredienti.py::test_create_ingrediente_success -v
```

### 3. Test Individuali
```bash
# Test solo struttura
pytest test_api_ingredienti.py::test_router_registration -v

# Test solo funzionalità CRUD
pytest test_api_ingredienti.py::test_create_ingrediente_success -v
pytest test_api_ingredienti.py::test_update_ingrediente_partial -v
pytest test_api_ingredienti.py::test_delete_soft_delete -v

# Test integrazione
pytest test_api_ingredienti.py::test_database_manager_usage -v
pytest test_api_ingredienti.py::test_model_methods_usage -v
```

### 4. Test Performance
```bash
# Test di performance e concorrenza
pytest test_api_ingredienti.py::test_get_ingredienti_performance -v
pytest test_api_ingredienti.py::test_concurrent_requests -v
```

## 🔍 Cosa VERIFICANO I TEST

### ✅ Verifica Strutturale
- Registrazione router `/ingredienti` nell'app FastAPI
- Presenza di tutti gli endpoint CRUD
- Disponibilità dei metodi HTTP corretti
- Connessione al database funzionante
- Disponibilità dei models e schemas

### ✅ Verifica Funzionale
- **GET /ingredienti**: Restituisce 200 e lista JSON
- **POST /ingredienti**: Creazione ingrediente valido
- **POST duplicato**: Errore 409 per nomi duplicati
- **PUT parziale**: Aggiorna solo campi specificati
- **PUT vuoto**: Errore 400 per body vuoto
- **DELETE soft delete**: Non elimina fisicamente il record

### ✅ Verifica Database
- Il record rimane nel database dopo DELETE
- Campo `attiva` impostato a 0 dopo soft delete
- L'ingrediente eliminato non appare più nelle API

### ✅ Verifica Integrazione
- Utilizzo di `DatabaseManager.get_connection()`
- Utilizzo dei metodi del model `Ingrediente`
- Pattern architetturali corretti

## 📊 OUTPUT DEI TEST

### Successo Esempio
```
🧪 ESECUZIONE TEST API INGREDIENTI
==================================================
test_router_registration.py::test_router_registration PASSED
test_api_ingredienti.py::test_get_ingredienti_success PASSED
test_api_ingredienti.py::test_create_ingrediente_success PASSED
test_api_ingredienti.py::test_delete_soft_delete PASSED
...
4 passed in 0.23s
```

### Errore Esempio
```
test_api_ingredienti.py::test_create_ingrediente_duplicate FAILED
Expected 409 for duplicate, got 200
```

## 🛠️ TROUBLESHOOTING

### Errore: "App non disponibile"
```bash
# Verifica che main.py esista e sia importabile
python -c "from main import app; print('OK')"
```

### Errore: Database non funzionante
```bash
# Verifica connessione database
python verify_structure.py
```

### Errore: Import falliti
```bash
# Verifica PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python verify_structure.py
```

## 📝 NOTE SUI TEST

### Database di Test
- I test creano un database pulito automaticamente
- Vengono inseriti dati di test predefiniti
- Il database viene pulito dopo ogni sessione di test

### Isolamento Test
- Ogni test è indipendente dagli altri
- Il database viene reinizializzato tra i test
- Nessun effetto collaterale tra test

### Performance
- I test includono verifiche di performance base
- Test di concorrenza per verificare robustezza
- Limite di 1 secondo per richieste GET

## 🎯 OBIETTIVI DEI TEST

1. **Automazione**: Verifica automatica senza intervento manuale
2. **Completezza**: Copertura di tutti gli aspetti richiesti
3. **Affidabilità**: Test isolati e ripetibili
4. **Chiarezza**: Output chiaro e di facile interpretazione
5. **Manutenibilità**: Codice di test facile da capire e modificare

## 📈 REPORT FINALE

Dopo l'esecuzione, i test forniranno un report completo su:
- ✅ Struttura corretta del progetto
- ✅ Funzionalità API implementate correttamente
- ✅ Integrazione con architettura esistente
- ✅ Comportamento soft delete verificato
- ✅ Performance e robustezza del sistema
