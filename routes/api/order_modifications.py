from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from core.database import DatabaseManager
from models import Ingrediente

router = APIRouter(prefix="/orders", tags=["order_modifications"])

def get_price_rules():
    """Ottiene le regole di prezzo per le modifiche"""
    with DatabaseManager.get_connection() as conn:
        rules = conn.execute("""
            SELECT tipo_ingrediente, prezzo_aggiunta, prezzo_rimozione 
            FROM regole_prezzo_modifiche 
            WHERE attiva = 1
        """).fetchall()
        
        return {row["tipo_ingrediente"]: {
            "aggiunta": row["prezzo_aggiunta"], 
            "rimozione": row["prezzo_rimozione"]
        } for row in rules}

def get_item_modifications(order_detail_id: int):
    """Ottiene le modifiche per un item dell'ordine"""
    with DatabaseManager.get_connection() as conn:
        modifications = conn.execute("""
            SELECT odm.azione, i.id, i.nome, i.tipo, odm.prezzo_modifica
            FROM ordine_dettagli_modifiche odm
            JOIN ingredienti i ON odm.ingrediente_id = i.id
            WHERE odm.ordine_dettagli_id = ?
        """, (order_detail_id,)).fetchall()
        
        return {
            "aggiunti": [m for m in modifications if m["azione"] == "aggiunto"],
            "rimossi": [m for m in modifications if m["azione"] == "rimosso"]
        }

@router.get("/price-rules")
def get_price_rules_endpoint():
    """Endpoint per ottenere le regole di prezzo"""
    return get_price_rules()

@router.patch("/price-rules/{ingredient_type}")
def update_price_rule(ingredient_type: str, data: dict):
    """Aggiorna regola prezzo per tipo ingrediente"""
    with DatabaseManager.get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO regole_prezzo_modifiche 
            (tipo_ingrediente, prezzo_aggiunta, prezzo_rimozione, attiva) 
            VALUES (?, ?, ?, 1)
        """, (ingredient_type, data.get("aggiunta", 1.0), data.get("rimozione", 0.5)))
        
        return {"success": True, "message": f"Regola per {ingredient_type} aggiornata"}

# Sposto gli endpoint specifici dopo quelli generici per evitare conflitti
@router.get("/{order_id}/items/{item_id}/ingredients")
def get_item_ingredients(order_id: int, item_id: int):
    """Ottieni gli ingredienti di un item con stato corrente"""
    with DatabaseManager.get_connection() as conn:
        # Verifica che l'item appartenga all'ordine
        item = conn.execute("""
            SELECT od.id, od.pizza_id, od.prezzo_unitario, od.prezzo_personalizzato
            FROM ordine_dettagli od
            WHERE od.ordine_id = ? AND od.pizza_id = ?
        """, (order_id, item_id)).fetchone()
        
        if not item:
            raise HTTPException(404, "Item non trovato nell'ordine")
        
        # Ottieni ingredienti originali della pizza
        original_ingredients = conn.execute("""
            SELECT i.id, i.nome, i.tipo
            FROM ingredienti i
            JOIN menu_item_ingredienti mii ON i.id = mii.ingrediente_id
            WHERE mii.menu_item_id = ?
        """, (item_id,)).fetchall()
        
        # Ottieni modifiche applicate
        modifications = get_item_modifications(item["id"])
        
        # Calcola stato corrente ingredienti
        added_ids = {m["id"] for m in modifications["aggiunti"]}
        removed_ids = {m["id"] for m in modifications["rimossi"]}
        
        current_ingredients = []
        available_ingredients = []
        
        # Ingredienti originali (non rimossi)
        for ing in original_ingredients:
            if ing["id"] not in removed_ids:
                current_ingredients.append({
                    "id": ing["id"],
                    "nome": ing["nome"],
                    "tipo": ing["tipo"],
                    "originale": True
                })
            else:
                available_ingredients.append({
                    "id": ing["id"],
                    "nome": ing["nome"],
                    "tipo": ing["tipo"],
                    "originale": True
                })
        
        # Tutti gli ingredienti disponibili (esclusi quelli già aggiunti)
        all_ingredients = Ingrediente.get_all()
        for ing in all_ingredients:
            if ing.id not in added_ids and ing.id not in {i["id"] for i in current_ingredients}:
                available_ingredients.append({
                    "id": ing.id,
                    "nome": ing.nome,
                    "tipo": ing.tipo,
                    "originale": False
                })
        
        return {
            "item_id": item["id"],
            "pizza_id": item_id,
            "prezzo_base": item["prezzo_unitario"],
            "prezzo_personalizzato": item["prezzo_personalizzato"],
            "current_ingredients": current_ingredients,
            "available_ingredients": available_ingredients,
            "modifications": modifications
        }

@router.post("/{order_id}/items/{item_id}/modify")
def modify_item_ingredients(order_id: int, item_id: int, data: dict):
    """Modifica gli ingredienti di un item dell'ordine"""
    with DatabaseManager.get_connection() as conn:
        # Verifica che l'item appartenga all'ordine
        item = conn.execute("""
            SELECT od.id, od.prezzo_unitario
            FROM ordine_dettagli od
            WHERE od.ordine_id = ? AND od.pizza_id = ?
        """, (order_id, item_id)).fetchone()
        
        if not item:
            raise HTTPException(404, "Item non trovato nell'ordine")
        
        item_detail_id = item["id"]
        prezzo_base = item["prezzo_unitario"]
        
        # Pulisci modifiche esistenti
        conn.execute("DELETE FROM ordine_dettagli_modifiche WHERE ordine_dettagli_id = ?", (item_detail_id,))
        
        # Ottieni regole prezzo
        price_rules = get_price_rules()
        
        # Applica nuove modifiche
        added_ingredients = data.get("added_ingredients", [])
        removed_ingredients = data.get("removed_ingredients", [])
        
        total_modification = 0
        modification_notes = []
        
        # Processa ingredienti aggiunti
        for ing_id in added_ingredients:
            ing = conn.execute("SELECT nome, tipo FROM ingredienti WHERE id = ?", (ing_id,)).fetchone()
            if not ing:
                continue
                
            rule = price_rules.get(ing["tipo"], price_rules.get("altro", {"aggiunta": 1.0, "rimozione": 0.5}))
            price_change = rule["aggiunta"]
            
            conn.execute("""
                INSERT INTO ordine_dettagli_modifiche 
                (ordine_dettagli_id, ingrediente_id, azione, prezzo_modifica) 
                VALUES (?, ?, 'aggiunto', ?)
            """, (item_detail_id, ing_id, price_change))
            
            total_modification += price_change
            modification_notes.append(f"+{ing['nome']}")
        
        # Processa ingredienti rimossi
        for ing_id in removed_ingredients:
            ing = conn.execute("SELECT nome, tipo FROM ingredienti WHERE id = ?", (ing_id,)).fetchone()
            if not ing:
                continue
                
            rule = price_rules.get(ing["tipo"], price_rules.get("altro", {"aggiunta": 1.0, "rimozione": 0.5}))
            price_change = -rule["rimozione"]  # Negativo perché è una rimozione
            
            conn.execute("""
                INSERT INTO ordine_dettagli_modifiche 
                (ordine_dettagli_id, ingrediente_id, azione, prezzo_modifica) 
                VALUES (?, ?, 'rimosso', ?)
            """, (item_detail_id, ing_id, abs(price_change)))
            
            total_modification += price_change
            modification_notes.append(f"-{ing['nome']}")
        
        # Calcola nuovo prezzo personalizzato
        new_price = prezzo_base + total_modification
        
        # Aggiorna prezzo personalizzato e note
        conn.execute("""
            UPDATE ordine_dettagli 
            SET prezzo_personalizzato = ?, note_modifiche = ?
            WHERE id = ?
        """, (new_price, ", ".join(modification_notes) if modification_notes else None, item_detail_id))
        
        return {
            "success": True,
            "prezzo_base": prezzo_base,
            "prezzo_personalizzato": new_price,
            "modifica_totale": total_modification,
            "modifiche": modification_notes,
            "dettagli_modifiche": get_item_modifications(item_detail_id)
        }
