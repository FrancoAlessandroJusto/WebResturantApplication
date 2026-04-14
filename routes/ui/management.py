# =========================
# IMPORT
# =========================

import os
import sqlite3
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.database import get_conn, BASE_DIR


# =========================
# ROUTER MANAGEMENT UI
# =========================

router = APIRouter(prefix="/mgmt", tags=["management_ui"])
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# =========================
# GET: pagina management (HTML)
# =========================

@router.get("/ui", response_class=HTMLResponse)
def mgmt_ui(request: Request):
    # 1) legge tutti gli item dal DB con ingredienti
    from models import MenuItem, Ingrediente
    
    try:
        # Usa il modello MenuItem per caricare dati completi
        menu_items = MenuItem.get_all()
        
        # 2) converte in lista di dict con ingredienti
        items = [item.to_dict() for item in menu_items]
        
    except Exception as e:
        # Fallback: carica solo dati base se c'è errore
        conn = get_conn()
        rows = conn.execute(
            "SELECT id, nome, prezzo, categoria FROM menu_items WHERE attiva = 1 ORDER BY categoria, nome"
        ).fetchall()
        conn.close()
        
        # Converte le righe in lista di dict senza ingredienti
        items = [{"id": r["id"], "nome": r["nome"], "prezzo": r["prezzo"], "categoria": r["categoria"], "ingredienti": []} for r in rows]

    # 3) renderizza management.html passando gli items
    return templates.TemplateResponse(
        "management.html",
        {"request": request, "items": items, "msg": None, "ok": True}
    )


# =========================
# POST: submit form "Aggiungi pizza" (HTML)
# =========================

@router.post("/ui/items/create", response_class=HTMLResponse)
async def mgmt_ui_create(
    request: Request,
    nome: str = Form(...),
    prezzo: float = Form(...),
    categoria: str = Form(...)
):
    try:
        # 1) inserisce il nuovo item nel DB
        conn = get_conn()
        conn.execute(
            "INSERT INTO menu_items (nome, prezzo, categoria) VALUES (?, ?, ?)",
            (nome, prezzo, categoria)
        )
        conn.commit()
        conn.close()

        msg = f"✅ '{nome}' aggiunto al menù nella categoria {categoria}!"
        ok = True

    except sqlite3.IntegrityError as e:
        # errore di vincolo (nome duplicato)
        msg = f"❌ Errore: '{nome}' esiste già nel menù!"
        ok = False

    except Exception as e:
        # qualsiasi altro errore
        msg = f"❌ Errore generico: {str(e)}"
        ok = False

    # 2) ricarica TUTTI gli item dal DB
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, nome, prezzo, categoria FROM menu_items WHERE attiva = 1 ORDER BY categoria, nome"
    ).fetchall()
    conn.close()

    items = [{"id": r["id"], "nome": r["nome"], "prezzo": r["prezzo"], "categoria": r["categoria"]} for r in rows]

    return templates.TemplateResponse(
        "management.html",
        {"request": request, "items": items, "msg": msg, "ok": ok}
    )


# =========================
# DELETE: elimina menu item
# =========================

@router.delete("/items/{item_id}")
def delete_menu_item(item_id: int):
    try:
        conn = get_conn()
        
        # Prima controlla se l'item esiste
        item = conn.execute(
            "SELECT nome FROM menu_items WHERE id = ?", (item_id,)
        ).fetchone()
        
        if not item:
            conn.close()
            return {"detail": "Articolo non trovato"}, 404
        
        # Disattiva l'item (soft delete)
        conn.execute(
            "UPDATE menu_items SET attiva = 0 WHERE id = ?",
            (item_id,)
        )
        conn.commit()
        conn.close()
        
        return {"message": "Articolo eliminato con successo"}
        
    except Exception as e:
        return {"detail": f"Errore durante l'eliminazione: {str(e)}"}, 500
