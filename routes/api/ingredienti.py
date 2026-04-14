from fastapi import APIRouter, HTTPException
from typing import List
from models import Ingrediente

router = APIRouter(prefix="/ingredienti", tags=["ingredienti"])

@router.get("", response_model=List[dict])
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

@router.get("/{ingrediente_id}", response_model=dict)
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
async def create_ingrediente(ingrediente_data: dict):
    """
    Crea un nuovo ingrediente con tutti i campi
    """
    if 'nome' not in ingrediente_data or not ingrediente_data['nome'].strip():
        raise HTTPException(status_code=400, detail="Campo 'nome' obbligatorio")
    
    try:
        nome = ingrediente_data['nome'].strip()
        tipo = ingrediente_data.get('tipo', 'altro')
        costo_unitario = float(ingrediente_data.get('costo_unitario', 0.0))
        unita_riferimento = ingrediente_data.get('unita_riferimento', 'pz')
        quantita_riferimento = float(ingrediente_data.get('quantita_riferimento', 1.0))
        
        # Controlla se esiste già
        ingredienti_esistenti = Ingrediente.get_all()
        if any(ing.nome.lower() == nome.lower() for ing in ingredienti_esistenti):
            raise HTTPException(status_code=400, detail="Ingrediente con questo nome già esistente")
        
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
async def update_ingrediente(ingrediente_id: int, ingrediente_data: dict):
    """
    Aggiorna un ingrediente esistente
    """
    if 'nome' not in ingrediente_data or not ingrediente_data['nome'].strip():
        raise HTTPException(status_code=400, detail="Campo 'nome' obbligatorio")
    
    try:
        nome = ingrediente_data['nome'].strip()
        tipo = ingrediente_data.get('tipo', 'altro')
        costo_unitario = float(ingrediente_data.get('costo_unitario', 0.0))
        unita_riferimento = ingrediente_data.get('unita_riferimento', 'pz')
        quantita_riferimento = float(ingrediente_data.get('quantita_riferimento', 1.0))
        
        # Controlla se l'ingrediente esiste
        ingredienti_esistenti = Ingrediente.get_all()
        ingrediente_da_aggiornare = next((ing for ing in ingredienti_esistenti if ing.id == ingrediente_id), None)
        
        if not ingrediente_da_aggiornare:
            raise HTTPException(status_code=404, detail="Ingrediente non trovato")
        
        # Controlla se il nuovo nome esiste (escludendo l'ingrediente corrente)
        if any(ing.nome.lower() == nome.lower() and ing.id != ingrediente_id for ing in ingredienti_esistenti):
            raise HTTPException(status_code=400, detail="Ingrediente con questo nome già esistente")
        
        # Aggiorna l'ingrediente nel database
        from core.database import get_conn
        conn = get_conn()
        conn.execute(
            "UPDATE ingredienti SET nome=?, tipo=?, costo_unitario=?, unita_riferimento=?, quantita_riferimento=? WHERE id=?",
            (nome, tipo, costo_unitario, unita_riferimento, quantita_riferimento, ingrediente_id)
        )
        conn.commit()
        conn.close()
        
        # Restituisci l'ingrediente aggiornato
        return {
            "id": ingrediente_id,
            "nome": nome,
            "tipo": tipo,
            "costo_unitario": costo_unitario,
            "unita_riferimento": unita_riferimento,
            "quantita_riferimento": quantita_riferimento,
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
