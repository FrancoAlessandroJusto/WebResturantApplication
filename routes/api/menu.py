from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import sqlite3

from core.database import DatabaseManager
from models import MenuItem, Ingrediente
from schemas import MenuItemCreate, MenuItemUpdate, MenuItemOut

router = APIRouter(prefix="/menu", tags=["menu"])

@router.get("", response_model=List[MenuItemOut])
def list_menu_items():
    """
    Restituisce tutti gli articoli del menù attivi con ingredienti
    """
    items = MenuItem.get_all()
    return [item.to_dict() for item in items]

@router.get("/{item_id}", response_model=MenuItemOut)
def get_menu_item(item_id: int):
    """
    Restituisce un singolo articolo del menù
    """
    items = MenuItem.get_all()
    item = next((item for item in items if item.id == item_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
        
    return item.to_dict()

@router.post("", response_model=dict)
def create_menu_item(item_data: MenuItemCreate):
    """
    Crea un nuovo articolo nel menù con ingredienti
    """
    try:
        nome = item_data.nome.strip()
        prezzo = item_data.prezzo
        categoria = item_data.categoria.value
        ingredienti_selezionati = item_data.ingredienti or []
        
        # Controlla se il nome esiste già (case insensitive)
        with DatabaseManager.get_connection() as conn:
            existing = conn.execute(
                "SELECT id FROM menu_items WHERE LOWER(nome) = LOWER(?) AND attiva = 1", 
                (nome,)
            ).fetchone()
        
        if existing:
            raise HTTPException(status_code=409, detail=f"Articolo '{nome}' già esistente nel menù")
        
        # Crea nuovo menu item
        nuovo_item = MenuItem.create(nome, prezzo, categoria, ingredienti_selezionati)
        
        return {
            "id": nuovo_item.id,
            "nome": nuovo_item.nome,
            "prezzo": nuovo_item.prezzo,
            "categoria": nuovo_item.categoria,
            "ingredienti": [ing.to_dict() for ing in nuovo_item.ingredienti],
            "message": "Articolo creato con successo"
        }
        
    except HTTPException:
        raise
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: menu_items.nome" in str(e):
            raise HTTPException(status_code=409, detail=f"Articolo '{nome}' già esistente nel menù")
        else:
            raise HTTPException(status_code=500, detail=f"Errore database: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la creazione: {str(e)}")

@router.put("/{item_id}", response_model=dict)
def update_menu_item(item_id: int, item_data: MenuItemUpdate):
    """
    Aggiorna un articolo esistente nel menù
    """
    try:
        import sqlite3
        from core.database import get_conn
        
        conn = get_conn()
        
        # Verifica se l'item esiste
        item = conn.execute(
            "SELECT id FROM menu_items WHERE id = ? AND attiva = 1", 
            (item_id,)
        ).fetchone()
        
        if not item:
            conn.close()
            raise HTTPException(status_code=404, detail="Articolo non trovato")
        
        # Prepara i valori aggiornati mantenendo quelli attuali
        nome = item_data.nome
        prezzo = item_data.prezzo
        categoria = item_data.categoria.value if item_data.categoria is not None else None

        if nome is not None:
            nome = nome.strip()

        # Aggiorna i campi solo se forniti, altrimenti si mantengono invariati
        if nome is not None or prezzo is not None or categoria is not None:
            conn.execute(
                "UPDATE menu_items SET nome = COALESCE(NULLIF(?, ''), nome), prezzo = COALESCE(?, prezzo), categoria = COALESCE(NULLIF(?, ''), categoria) WHERE id = ?",
                (nome, prezzo, categoria, item_id)
            )
        
        # Gestione ingredienti (se presenti)
        if item_data.ingredienti is not None:
            # Rimuovi ingredienti esistenti
            conn.execute("DELETE FROM menu_item_ingredienti WHERE menu_item_id = ?", (item_id,))
            
            # Aggiungi nuovi ingredienti
            for ing in item_data.ingredienti:
                conn.execute(
                    "INSERT INTO menu_item_ingredienti (menu_item_id, ingrediente_id, quantita) VALUES (?, ?, ?)",
                    (item_id, ing.ingrediente_id, ing.quantita)
                )
        
        conn.commit()
        conn.close()
        
        return {"message": "Articolo aggiornato con successo"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'aggiornamento: {str(e)}")

@router.delete("/{item_id}")
def delete_menu_item(item_id: int):
    """
    Disattiva un menu item (soft delete)
    """
    try:
        import sqlite3
        from core.database import get_conn
        
        conn = get_conn()
        
        # Controlla se l'item esiste
        item = conn.execute(
            "SELECT nome FROM menu_items WHERE id = ?", (item_id,)
        ).fetchone()
        
        if not item:
            conn.close()
            raise HTTPException(status_code=404, detail="Articolo non trovato")
        
        # Disattiva l'item
        conn.execute(
            "UPDATE menu_items SET attiva = 0 WHERE id = ?",
            (item_id,)
        )
        conn.commit()
        conn.close()
        
        return {"message": f"Articolo '{item['nome']}' eliminato con successo"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'eliminazione: {str(e)}")
