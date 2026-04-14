# =========================
# API ROUTER: GESTIONE INGREDIENTI
# =========================

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
import sqlite3

from core.database import DatabaseManager
from models import Ingrediente

# =========================
# PYDANTIC SCHEMAS
# =========================

class IngredienteCreate(BaseModel):
    """
    Schema per la creazione di un nuovo ingrediente
    """
    nome: str = Field(min_length=1, max_length=100, description="Nome dell'ingrediente")
    tipo: str = Field(default="altro", description="Tipo di ingrediente")
    costo_unitario: float = Field(default=0.0, ge=0, description="Costo unitario")
    unita_riferimento: str = Field(default="pz", description="Unità di riferimento")
    quantita_riferimento: float = Field(default=1.0, gt=0, description="Quantità di riferimento")

class IngredienteUpdate(BaseModel):
    """
    Schema per l'aggiornamento di un ingrediente esistente
    """
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[str] = None
    costo_unitario: Optional[float] = Field(None, ge=0)
    unita_riferimento: Optional[str] = None
    quantita_riferimento: Optional[float] = Field(None, gt=0)

class IngredienteResponse(BaseModel):
    """
    Schema per la risposta API
    """
    id: int
    nome: str
    tipo: str
    costo_unitario: float
    unita_riferimento: str
    quantita_riferimento: float
    attiva: bool

# =========================
# ROUTER SETUP
# =========================

router = APIRouter(prefix="/ingredienti", tags=["ingredienti"])

# =========================
# API ENDPOINTS
# =========================

@router.get("", response_model=List[IngredienteResponse])
def list_ingredienti():
    """
    Restituisce tutti gli ingredienti attivi
    """
    try:
        ingredienti = Ingrediente.get_all()
        return [IngredienteResponse(**ing.to_dict()) for ing in ingredienti]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante il caricamento: {str(e)}")

@router.get("/{ingrediente_id}", response_model=IngredienteResponse)
def get_ingrediente(ingrediente_id: int):
    """
    Restituisce un singolo ingrediente per ID
    """
    try:
        with DatabaseManager.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM ingredienti WHERE id = ? AND attiva = 1", 
                (ingrediente_id,)
            ).fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Ingrediente non trovato")
            
            ingrediente = Ingrediente.from_db(row)
            return IngredienteResponse(**ingrediente.to_dict())
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante il caricamento: {str(e)}")

@router.post("", response_model=IngredienteResponse)
def create_ingrediente(ingrediente_data: IngredienteCreate):
    """
    Crea un nuovo ingrediente
    """
    try:
        with DatabaseManager.get_connection() as conn:
            # Controlla se il nome esiste già (case insensitive)
            existing = conn.execute(
                "SELECT id FROM ingredienti WHERE LOWER(nome) = LOWER(?) AND attiva = 1", 
                (ingrediente_data.nome.strip(),)
            ).fetchone()
            
            if existing:
                raise HTTPException(status_code=409, detail=f"Ingrediente '{ingrediente_data.nome}' già esistente")
            
            # Crea nuovo ingrediente
            nuovo_ingrediente = Ingrediente.create(
                nome=ingrediente_data.nome.strip(),
                tipo=ingrediente_data.tipo,
                costo_unitario=ingrediente_data.costo_unitario,
                unita_riferimento=ingrediente_data.unita_riferimento,
                quantita_riferimento=ingrediente_data.quantita_riferimento
            )
            
            return IngredienteResponse(**nuovo_ingrediente.to_dict())
            
    except HTTPException:
        raise
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="Ingrediente con questo nome già esistente")
        else:
            raise HTTPException(status_code=500, detail=f"Errore database: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la creazione: {str(e)}")

@router.put("/{ingrediente_id}", response_model=IngredienteResponse)
def update_ingrediente(ingrediente_id: int, ingrediente_data: IngredienteUpdate):
    """
    Aggiorna un ingrediente esistente
    """
    try:
        with DatabaseManager.get_connection() as conn:
            # Verifica se l'ingrediente esiste
            existing = conn.execute(
                "SELECT * FROM ingredienti WHERE id = ? AND attiva = 1", 
                (ingrediente_id,)
            ).fetchone()
            
            if not existing:
                raise HTTPException(status_code=404, detail="Ingrediente non trovato")
            
            # Prepara i dati per l'aggiornamento
            update_data = ingrediente_data.dict(exclude_unset=True)
            
            if not update_data:
                raise HTTPException(status_code=400, detail="Nessun dato fornito per l'aggiornamento")
            
            # Controlla duplicato nome se viene aggiornato
            if 'nome' in update_data:
                nome_check = update_data['nome'].strip()
                duplicate = conn.execute(
                    "SELECT id FROM ingredienti WHERE LOWER(nome) = LOWER(?) AND id != ? AND attiva = 1",
                    (nome_check, ingrediente_id)
                ).fetchone()
                
                if duplicate:
                    raise HTTPException(status_code=409, detail=f"Ingrediente '{nome_check}' già esistente")
                
                update_data['nome'] = nome_check
            
            # Costruisce la query di aggiornamento dinamica
            set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values()) + [ingrediente_id]
            
            conn.execute(
                f"UPDATE ingredienti SET {set_clause} WHERE id = ?",
                values
            )
            
            # Recupera l'ingrediente aggiornato
            updated_row = conn.execute(
                "SELECT * FROM ingredienti WHERE id = ?", 
                (ingrediente_id,)
            ).fetchone()
            
            updated_ingrediente = Ingrediente.from_db(updated_row)
            return IngredienteResponse(**updated_ingrediente.to_dict())
            
    except HTTPException:
        raise
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="Ingrediente con questo nome già esistente")
        else:
            raise HTTPException(status_code=500, detail=f"Errore database: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'aggiornamento: {str(e)}")

@router.delete("/{ingrediente_id}")
def delete_ingrediente(ingrediente_id: int):
    """
    Disattiva un ingrediente (soft delete)
    """
    try:
        with DatabaseManager.get_connection() as conn:
            # Verifica se l'ingrediente esiste
            ingrediente = conn.execute(
                "SELECT nome FROM ingredienti WHERE id = ? AND attiva = 1", 
                (ingrediente_id,)
            ).fetchone()
            
            if not ingrediente:
                raise HTTPException(status_code=404, detail="Ingrediente non trovato")
            
            # Soft delete: imposta attiva = 0
            conn.execute(
                "UPDATE ingredienti SET attiva = 0 WHERE id = ?",
                (ingrediente_id,)
            )
            
            return {"message": f"Ingrediente '{ingrediente['nome']}' eliminato con successo"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'eliminazione: {str(e)}")
