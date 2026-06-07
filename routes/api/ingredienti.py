from fastapi import APIRouter, HTTPException
from typing import List
from models import Ingrediente
from schemas import IngredienteCreate, IngredienteUpdate, IngredienteOut

router = APIRouter(prefix="/ingredienti", tags=["ingredienti"])

@router.get("", response_model=List[IngredienteOut])
def list_ingredienti():
    """
    Restituisce tutti gli ingredienti attivi
    """
    try:
        # recupera i dati dal database
        ingredienti = Ingrediente.get_all()
        # debug server: stampo quante righe ho ricevuto
        print(f"[DEBUG] /ingredienti chiamato, {len(ingredienti)} ingredienti trovati")
        return [ing.to_dict() for ing in ingredienti]
    except Exception as e:
        # log dell'errore in console server
        print(f"[ERROR] eccezione in list_ingredienti: {e}")
        raise HTTPException(status_code=500, detail=f"Errore durante il caricamento: {str(e)}")

@router.get("/{ingrediente_id}", response_model=IngredienteOut)
def get_ingrediente(ingrediente_id: int):
    """
    Restituisce un singolo ingrediente per l'edit
    """
    try:
        ingredienti = Ingrediente.get_all()
        ingrediente = next((ing for ing in ingredienti if ing.id == ingrediente_id), None)
        
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente non trovato")
        
        return ingrediente.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] eccezione in get_ingrediente: {e}")
        raise HTTPException(status_code=500, detail=f"Errore durante il caricamento: {str(e)}")

@router.post("", response_model=dict)
async def create_ingrediente(ingrediente_data: IngredienteCreate):
    """
    Crea un nuovo ingrediente con tutti i campi
    """
    try:
        nome = ingrediente_data.nome.strip()
        tipo = ingrediente_data.tipo.value if hasattr(ingrediente_data.tipo, 'value') else ingrediente_data.tipo
        costo_unitario = ingrediente_data.costo_unitario
        unita_riferimento = ingrediente_data.unita_riferimento.value if hasattr(ingrediente_data.unita_riferimento, 'value') else ingrediente_data.unita_riferimento
        quantita_riferimento = ingrediente_data.quantita_riferimento
        
        # Controlla se esiste già (case-insensitive)
        ingredienti_esistenti = Ingrediente.get_all()
        if any(ing.nome.lower() == nome.lower() for ing in ingredienti_esistenti):
            raise HTTPException(status_code=409, detail="Ingrediente con questo nome già esistente")
        
        # Crea nuovo ingrediente
        nuovo_ingrediente = Ingrediente.create(
            nome=nome,
            tipo=tipo,
            costo_unitario=costo_unitario,
            unita_riferimento=unita_riferimento,
            quantita_riferimento=quantita_riferimento
        )
        
        return {
            "id": nuovo_ingrediente.id,
            "nome": nuovo_ingrediente.nome,
            "tipo": nuovo_ingrediente.tipo,
            "costo_unitario": nuovo_ingrediente.costo_unitario,
            "unita_riferimento": nuovo_ingrediente.unita_riferimento,
            "quantita_riferimento": nuovo_ingrediente.quantita_riferimento,
            "message": "Ingrediente creato con successo"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] eccezione in create_ingrediente: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Errore durante la creazione: {str(e)}")

@router.put("/{ingrediente_id}", response_model=dict)
async def update_ingrediente(ingrediente_id: int, ingrediente_data: IngredienteUpdate):
    """
    Aggiorna un ingrediente esistente (supporta aggiornamenti parziali)
    """
    updated_data = ingrediente_data.model_dump(exclude_none=True)
    if not updated_data:
        raise HTTPException(status_code=400, detail="Nessun dato fornito per l'aggiornamento")

    try:
        from core.database import get_conn
        conn = get_conn()

        # Controlla se l'ingrediente esiste
        row = conn.execute(
            "SELECT * FROM ingredienti WHERE id = ?",
            (ingrediente_id,)
        ).fetchone()

        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Ingrediente non trovato")

        # Valori correnti
        current = dict(row)

        # Costruisci valori aggiornati (mantieni i valori correnti se non forniti)
        nome = updated_data.get('nome', current.get('nome'))
        if isinstance(nome, str):
            nome = nome.strip()

        tipo = updated_data.get('tipo', current.get('tipo', 'altro'))
        if hasattr(tipo, 'value'):
            tipo = tipo.value

        # Usa i valori forniti se presenti, altrimenti i valori correnti
        if 'costo_unitario' in updated_data:
            costo_unitario = float(updated_data.get('costo_unitario', 0.0))
        else:
            costo_unitario = float(current.get('costo_unitario', 0.0))

        unita_riferimento = updated_data.get('unita_riferimento', current.get('unita_riferimento', 'pz'))
        if hasattr(unita_riferimento, 'value'):
            unita_riferimento = unita_riferimento.value

        if 'quantita_riferimento' in updated_data:
            quantita_riferimento = float(updated_data.get('quantita_riferimento', 1.0))
        else:
            quantita_riferimento = float(current.get('quantita_riferimento', 1.0))

        # Controlla duplicato nome (escludendo l'ingrediente corrente)
        ingredienti_esistenti = Ingrediente.get_all()
        if nome and any(ing.nome.lower() == nome.lower() and ing.id != ingrediente_id for ing in ingredienti_esistenti):
            conn.close()
            raise HTTPException(status_code=409, detail="Ingrediente con questo nome già esistente")

        # Esegui update
        conn.execute(
            "UPDATE ingredienti SET nome=?, tipo=?, costo_unitario=?, unita_riferimento=?, quantita_riferimento=? WHERE id=?",
            (nome, tipo, costo_unitario, unita_riferimento, quantita_riferimento, ingrediente_id)
        )
        conn.commit()

        # Recupera nuova riga per risposta
        updated_row = conn.execute("SELECT * FROM ingredienti WHERE id = ?", (ingrediente_id,)).fetchone()
        conn.close()

        updated = dict(updated_row) if updated_row else {}

        return {
            "id": updated.get('id', ingrediente_id),
            "nome": updated.get('nome'),
            "tipo": updated.get('tipo'),
            "costo_unitario": updated.get('costo_unitario'),
            "unita_riferimento": updated.get('unita_riferimento'),
            "quantita_riferimento": updated.get('quantita_riferimento'),
            "message": "Ingrediente aggiornato con successo"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] eccezione in update_ingrediente: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Errore durante l'aggiornamento: {str(e)}")

@router.delete("/{ingrediente_id}")
def delete_ingrediente(ingrediente_id: int):
    """
    Disattiva un ingrediente (soft delete)
    """
    try:
        import sqlite3
        from core.database import get_conn
        
        conn = get_conn()
        
        # Controlla se l'ingrediente esiste
        ingrediente = conn.execute(
            "SELECT nome FROM ingredienti WHERE id = ?", (ingrediente_id,)
        ).fetchone()
        
        if not ingrediente:
            conn.close()
            raise HTTPException(status_code=404, detail="Ingrediente non trovato")
        
        # Disattiva l'ingrediente
        conn.execute(
            "UPDATE ingredienti SET attiva = 0 WHERE id = ?",
            (ingrediente_id,)
        )
        conn.commit()
        conn.close()
        
        return {"message": f"Ingrediente '{ingrediente['nome']}' eliminato con successo"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'eliminazione: {str(e)}")
