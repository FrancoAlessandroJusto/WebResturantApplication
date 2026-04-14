# 🐛 Problemi Noti e Correzioni da Fare

## 🔥 Problemi Critici (Urgenti)

### 1. **Ordinamento Tabella Ingredienti non Funziona**
**File**: `templates/analytics.html`
**Problema**: L'ordinamento nella tabella ingredienti non si applica correttamente
**Sintomi**: I dati rimangono disordinati nonostante il cambio del filtro
**Causa**: La funzione `filterAndSortIngredients()` non viene chiamata correttamente al caricamento
**Soluzione**:
```javascript
// In loadAnalytics(), dopo aver caricato i dati:
allIngredientsData = ingredientsData.ingredienti_analytics || [];
// Applica ordinamento di default
filterAndSortIngredients(); // Invece di updateIngredientsTable(allIngredientsData)
```

### 2. **Import mancante in main.py**
**File**: `main.py`
**Problema**: `from db import init_db` ma `db.py` è stato spostato in `tests_archive/`
**Soluzione**: Spostare `init_db()` in `core/database.py` o creare un nuovo file `database_init.py`

---

## ⚠️ Problemi Medi (Da risolvere presto)

### 3. **Indicatore Modifiche su Item Singolo**
**File**: `templates/orders.html`
**Problema**: L'indicatore 🔧 appare sul titolo ordine invece che sui singoli item
**Stato**: ✅ **RISOLTO** - Ora appare correttamente sui singoli item modificati

### 4. **Gestione Item Multipli con Prezzi Diversi**
**File**: `routes/api/orders.py`
**Problema**: Item con stesso pizza_id ma prezzi diversi vengono raggruppati
**Stato**: ✅ **RISOLTO** - Logica merge basata su prezzo_personalizzato

### 5. **Campo Coperto per Ordini Esistenti**
**File**: `templates/orders.html`
**Problema**: Viene mostrato anche se esiste già un ordine attivo
**Stato**: ✅ **RISOLTO** - Check esistente e nascondimento campo

---

## 🟡 Problemi Minori (Da risolvere quando possibile)

### 6. **Debug Logging in Produzione**
**File**: `templates/analytics.html`
**Problema**: Troppi `console.log()` in produzione
**Soluzione**: Rimuovere o commentare i log non essenziali

### 7. **Error Handling Frontend**
**File**: Tutti i template HTML
**Problema**: Messaggi di errore poco user-friendly
**Soluzione**: Migliorare UI per errori di rete/API

### 8. **Validazione Input Frontend**
**File**: `templates/orders.html`
**Problema**: Mancanza di validazione client-side
**Soluzione**: Aggiungere validation su quantità, note, etc.

---

## 🔧 Problemi Architetturali

### 9. **Dipendenze Circolari**
**File**: Vari
**Problema**: Alcuni import potrebbero creare dipendenze circolari
**Soluzione**: Review degli import e refactoring se necessario

### 10. **Gestione Concorrenza Database**
**File**: `core/database.py`
**Problema**: Mancanza di gestione lock per operazioni concorrenti
**Soluzione**: Implementare transaction locks per ordini simultanei

---

## 📱 Problemi UI/UX

### 11. **Responsive Design**
**File**: Tutti i template
**Problema**: Layout non ottimale per mobile
**Soluzione**: Review Tailwind classes per mobile-first

### 12. **Loading States**
**File**: Tutti i template
**Problema**: Mancanza di indicatori di caricamento
**Soluzione**: Aggiungere spinner/skeleton durante fetch

### 13. **Accessibility (a11y)**
**File**: Tutti i template
**Problema**: Mancanza di ARIA labels e keyboard navigation
**Soluzione**: Aggiungere attributi ARIA e focus management

---

## 🧪 Test e Qualità

### 14. **Suite Test Incompleta**
**File**: `tests/`
**Problema**: Mancanza di test unitari e integration test
**Soluzione**: Implementare pytest con fixtures

### 15. **Code Coverage**
**File**: Tutti i file Python
**Problema**: Code coverage basso
**Soluzione**: Aggiungere test per coprire tutti i metodi critici

---

## 🚀 Performance

### 16. **Query N+1 Problem**
**File**: `routes/api/analytics.py`
**Problema**: Query multiple per ingredienti/analytics
**Soluzione**: Ottimizzare con JOIN e aggregazioni

### 17. **Frontend Performance**
**File**: Template HTML
**Problema**: DOM manipulation inefficiente
**Soluzione**: Implementare virtual scrolling per tabelle grandi

---

## 📋 Checklist Correzioni Immediate

### 🔥 Da fare ORA:
- [ ] Correggere ordinamento tabella ingredienti
- [ ] Sistemare import database in main.py

### ⚠️ Da fare questa settimana:
- [ ] Testare tutte le funzionalità ordini
- [ ] Verificare indicatore modifiche item
- [ ] Testare nascondimento campo coperto

### 🟡 Da fare prossimamente:
- [ ] Pulire console.log production
- [ ] Migliorare error handling UI
- [ ] Aggiungere validazione input

---

## 🎯 Priorità Sviluppo

1. **Critical** (Bloccanti): Ordinamento ingredienti, import database
2. **High** (Funzionalità): Test completo sistema ordini
3. **Medium** (UX): Miglioramento UI/UX
4. **Low** (Technical): Refactoring, performance

---

## 📝 Note per Sviluppatori

### Testing Ordinamento Ingredienti:
```bash
# Test API
curl "http://127.0.0.1:8000/analytics/ingredients?periodo=today"

# Test Frontend
# 1. Aprire http://127.0.0.1:8000/analytics/ui
# 2. Cambiare ordinamento nel menu a tendina
# 3. Verificare che la tabella si riordini
```

### Testing Ordini:
```bash
# Test creazione ordini con modifiche
python tests_archive/test_ui_improvements.py
python tests_archive/test_separate_items.py
```

### Debug Database:
```bash
# Verificare tabelle
sqlite3 pizzeria.db ".schema"
sqlite3 pizzeria.db "SELECT * FROM ordini LIMIT 5"
```

---

## 🔍 Come Testare le Correzioni

1. **Ordinamento Ingredienti**:
   - Aprire analytics UI
   - Cambiare ordinamento nel dropdown
   - Verificare riordinamento tabella

2. **Sistema Ordini**:
   - Creare ordine con pizza normale
   - Aggiungere pizza modificata
   - Verificare item separati con indicatore

3. **Campo Coperto**:
   - Selezionare tavolo con ordine esistente
   - Verificare che campo coperto sia nascosto

---

## 📞 Supporto

Per problemi urgenti:
1. Controllare logs in console browser
2. Verificare logs server in terminale
3. Testare con curl/Postman
4. Review codice secondo guidelines in `CODE_STRUCTURE.md`
