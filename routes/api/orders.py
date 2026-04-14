# =========================
# IMPORT
# =========================

import sqlite3
from fastapi import APIRouter, HTTPException
from typing import List
import sys
from pathlib import Path
from datetime import datetime

from core.database import get_conn

# Aggiungi il percorso per i servizi
sys.path.append(str(Path(__file__).parent.parent))

try:
    from services.print_service import print_service, OrderStatus
    PRINT_SERVICE_AVAILABLE = True
except ImportError:
    PRINT_SERVICE_AVAILABLE = False
    print("Print service non disponibile - usando fallback")


# =========================
# ROUTER ORDERS API
# =========================

router = APIRouter(prefix="/orders", tags=["orders"])


# =========================
# ORDERS API
# =========================

@router.get("/menu", response_model=list[dict])
def get_menu():
    """
    Restituisce il menu completo per la presa ordini
    """
    conn = get_conn()
    
    rows = conn.execute(
        "SELECT id, nome, prezzo, categoria FROM menu_items WHERE attiva = 1 ORDER BY categoria, nome"
    ).fetchall()
    
    conn.close()
    
    menu = [
        {
            "id": r["id"],
            "nome": r["nome"], 
            "prezzo": r["prezzo"],
            "categoria": r["categoria"]
        }
        for r in rows
    ]
    
    return menu

@router.post("/")
def create_order(order_data: dict):
    """Crea un nuovo ordine o unisce a ordine esistente dello stesso tavolo"""
    conn = get_conn()
    
    try:
        # Verifica se esiste già un ordine attivo per questo tavolo
        existing_order = conn.execute("""
            SELECT id, numero_tavolo, totale, stato
            FROM ordini 
            WHERE numero_tavolo = ? AND stato = 'in_corso'
            ORDER BY data_ora DESC
            LIMIT 1
        """, (order_data["numero_tavolo"],)).fetchone()
        
        if existing_order:
            # Unisci l'ordine esistente
            return merge_with_existing_order(conn, existing_order, order_data)
        else:
            # Crea nuovo ordine
            return create_new_order(conn, order_data)
            
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(500, f"Errore database: {str(e)}")
    finally:
        conn.close()

def merge_with_existing_order(conn, existing_order, new_order_data):
    """Unisce nuovo ordine con ordine esistente dello stesso tavolo"""
    try:
        ordine_id = existing_order["id"]
        current_total = existing_order["totale"]
        
        # Processa i nuovi dettagli
        dettagli_data = []
        new_total = current_total
        
        for dettaglio in new_order_data["dettagli"]:
            # Verifica esistenza menu item e prezzo
            menu_item = conn.execute(
                "SELECT id, nome, prezzo FROM menu_items WHERE id = ? AND attiva = 1",
                (dettaglio["pizza_id"],)
            ).fetchone()
            
            if not menu_item:
                raise HTTPException(404, f"Articolo {dettaglio['pizza_id']} non trovato o non attivo")
            
            # Usa prezzo personalizzato se fornito, altrimenti prezzo base
            prezzo_da_usare = dettaglio.get("prezzo_personalizzato") or menu_item["prezzo"]
            subtotale = prezzo_da_usare * dettaglio["quantita"]
            new_total += subtotale
            
            # Verifica se l'articolo con le stesse modifiche esiste già nell'ordine
            prezzo_personalizzato_value = dettaglio.get("prezzo_personalizzato")
            
            if prezzo_personalizzato_value is None:
                # Cerca item senza modifiche
                existing_item = conn.execute("""
                    SELECT id, quantita, prezzo_personalizzato 
                    FROM ordine_dettagli 
                    WHERE ordine_id = ? AND pizza_id = ? AND prezzo_personalizzato IS NULL
                """, (ordine_id, dettaglio["pizza_id"])).fetchone()
            else:
                # Cerca item con stesso prezzo personalizzato
                existing_item = conn.execute("""
                    SELECT id, quantita, prezzo_personalizzato 
                    FROM ordine_dettagli 
                    WHERE ordine_id = ? AND pizza_id = ? AND prezzo_personalizzato = ?
                """, (ordine_id, dettaglio["pizza_id"], prezzo_personalizzato_value)).fetchone()
            
            if existing_item:
                # Aggiorna quantità esistente solo se prezzo personalizzato è identico
                new_quantita = existing_item["quantita"] + dettaglio["quantita"]
                
                conn.execute("""
                    UPDATE ordine_dettagli 
                    SET quantita = ?, note = COALESCE(?, note)
                    WHERE id = ?
                """, (new_quantita, dettaglio.get("note", ""), existing_item["id"]))
                
                dettagli_data.append({
                    "pizza_id": dettaglio["pizza_id"],
                    "pizza_nome": menu_item["nome"],
                    "quantita": new_quantita,
                    "note": dettaglio.get("note", ""),
                    "prezzo_unitario": menu_item["prezzo"],
                    "prezzo_personalizzato": prezzo_da_usare,
                    "subtotale": prezzo_da_usare * new_quantita
                })
            else:
                # Aggiungi nuovo articolo con prezzo personalizzato diverso
                conn.execute("""
                    INSERT INTO ordine_dettagli(ordine_id, pizza_id, quantita, note, prezzo_unitario, prezzo_personalizzato) 
                    VALUES(?, ?, ?, ?, ?, ?)
                """, (ordine_id, dettaglio["pizza_id"], dettaglio["quantita"], 
                      dettaglio.get("note", ""), menu_item["prezzo"], prezzo_da_usare if prezzo_da_usare != menu_item["prezzo"] else None))
                
                dettagli_data.append({
                    "pizza_id": dettaglio["pizza_id"],
                    "pizza_nome": menu_item["nome"],
                    "quantita": dettaglio["quantita"],
                    "note": dettaglio.get("note", ""),
                    "prezzo_unitario": menu_item["prezzo"],
                    "prezzo_personalizzato": prezzo_da_usare,
                    "subtotale": subtotale
                })
        
        # Aggiorna totale ordine
        conn.execute("""
            UPDATE ordini 
            SET totale = ? 
            WHERE id = ?
        """, (new_total, ordine_id))
        
        conn.commit()
        
        # Prepara risposta
        ordine = conn.execute("""
            SELECT id, numero_tavolo, data_ora, stato, totale FROM ordini WHERE id = ?
        """, (ordine_id,)).fetchone()
        
        return {
            "id": ordine["id"],
            "numero_tavolo": ordine["numero_tavolo"],
            "data_ora": ordine["data_ora"],
            "stato": ordine["stato"],
            "totale": ordine["totale"],
            "dettagli": dettagli_data,
            "merged": True,
            "message": f"Ordine unito al tavolo {ordine['numero_tavolo']}"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Errore unione ordine: {str(e)}")

def create_new_order(conn, order_data):
    """Crea un nuovo ordine (funzione originale)"""
    try:
        # Calcola il totale
        totale_ordine = 0.0
        dettagli_data = []
        
        for dettaglio in order_data["dettagli"]:
            # Verifica esistenza menu item e prezzo
            menu_item = conn.execute(
                "SELECT id, nome, prezzo FROM menu_items WHERE id = ? AND attiva = 1",
                (dettaglio["pizza_id"],)
            ).fetchone()
            
            if not menu_item:
                raise HTTPException(404, f"Articolo {dettaglio['pizza_id']} non trovato o non attivo")
            
            # Usa prezzo personalizzato se fornito, altrimenti prezzo base
            prezzo_da_usare = dettaglio.get("prezzo_personalizzato") or menu_item["prezzo"]
            subtotale = prezzo_da_usare * dettaglio["quantita"]
            totale_ordine += subtotale
            
            dettagli_data.append({
                "pizza_id": dettaglio["pizza_id"],
                "pizza_nome": menu_item["nome"],
                "quantita": dettaglio["quantita"],
                "note": dettaglio.get("note", ""),
                "prezzo_unitario": menu_item["prezzo"],
                "prezzo_personalizzato": prezzo_da_usare,
                "subtotale": subtotale
            })
        
        # Calcola il coperto (2€ a persona)
        numero_persone = order_data.get("numero_persone", 1)
        coperto = numero_persone * 2.0
        totale_finale = totale_ordine + coperto
        
        # Inserisci ordine con numero_persone e coperto
        cur = conn.execute(
            "INSERT INTO ordini(numero_tavolo, numero_persone, totale, coperto) VALUES(?, ?, ?, ?)",
            (order_data["numero_tavolo"], numero_persone, totale_finale, coperto)
        )
        ordine_id = cur.lastrowid
        
        # Inserisci dettagli ordine
        for dettaglio in order_data["dettagli"]:
            menu_item = conn.execute(
                "SELECT prezzo FROM menu_items WHERE id = ?",
                (dettaglio["pizza_id"],)
            ).fetchone()
            
            # Usa prezzo personalizzato se fornito, altrimenti prezzo base
            prezzo_da_usare = dettaglio.get("prezzo_personalizzato") or menu_item["prezzo"]
            
            conn.execute(
                "INSERT INTO ordine_dettagli(ordine_id, pizza_id, quantita, note, prezzo_unitario, prezzo_personalizzato) VALUES(?, ?, ?, ?, ?, ?)",
                (ordine_id, dettaglio["pizza_id"], dettaglio["quantita"], dettaglio.get("note", ""), menu_item["prezzo"], prezzo_da_usare if prezzo_da_usare != menu_item["prezzo"] else None)
            )
        
        conn.commit()
        
        # Prepara dati per risposta
        ordine = conn.execute(
            "SELECT id, numero_tavolo, data_ora, stato, totale FROM ordini WHERE id = ?",
            (ordine_id,)
        ).fetchone()
        
        order_response = {
            "id": ordine["id"],
            "numero_tavolo": ordine["numero_tavolo"],
            "data_ora": ordine["data_ora"],
            "stato": ordine["stato"],
            "totale": ordine["totale"],
            "dettagli": dettagli_data,
            "merged": False,
            "message": "Nuovo ordine creato"
        }
        
        # Salva statistiche
        if PRINT_SERVICE_AVAILABLE:
            print_service.save_to_statistics(order_response)
            
            # Aggiungi alla coda di stampa
            print_job = print_service.add_to_print_queue(order_response)
            
            # Processa stampa (asincrono in futuro)
            try:
                import asyncio
                # In produzione, questo dovrebbe essere un task background
                # asyncio.create_task(print_service.process_print_queue())
                print_job.status = OrderStatus.PRINTING
                
                # Per ora, stampa su console
                print_service.print_order_console(print_job)
                
            except Exception as print_error:
                print(f"Errore stampa: {print_error}")
        
        return order_response
        
    except Exception as e:
        raise HTTPException(500, f"Errore creazione ordine: {str(e)}")

@router.get("/{ordine_id}")
def get_order(ordine_id: int):
    """Ottiene i dettagli di un ordine"""
    conn = get_conn()
    
    try:
        ordine = conn.execute(
            "SELECT id, numero_tavolo, data_ora, stato, totale, COALESCE(numero_persone, 1) as numero_persone, COALESCE(coperto, 0) as coperto FROM ordini WHERE id = ?",
            (ordine_id,)
        ).fetchone()
        
        if not ordine:
            conn.close()
            raise HTTPException(404, "Ordine non trovato")
        
        # Prende dettagli
        det_rows = conn.execute("""
            SELECT od.pizza_id, mi.nome as pizza_nome, od.quantita, od.note, 
                   od.prezzo_unitario,
                   od.prezzo_personalizzato,
                   (od.quantita * COALESCE(od.prezzo_personalizzato, od.prezzo_unitario)) as subtotale,
                   COALESCE(od.served, 0) as served, od.note_modifiche
            FROM ordine_dettagli od
            JOIN menu_items mi ON od.pizza_id = mi.id
            WHERE od.ordine_id = ?
        """, (ordine_id,)).fetchall()
        
        conn.close()
        
        dettagli = [
            {
                "pizza_id": r["pizza_id"],
                "pizza_nome": r["pizza_nome"],
                "quantita": r["quantita"],
                "note": r["note"],
                "prezzo_unitario": r["prezzo_unitario"],
                "prezzo_personalizzato": r["prezzo_personalizzato"],
                "subtotale": r["subtotale"],
                "served": bool(r["served"]),
                "note_modifiche": r["note_modifiche"]
            }
            for r in det_rows
        ]
        
        return {
            "id": ordine["id"],
            "numero_tavolo": ordine["numero_tavolo"],
            "data_ora": ordine["data_ora"],
            "stato": ordine["stato"],
            "totale": ordine["totale"],
            "numero_persone": ordine["numero_persone"],
            "coperto": ordine["coperto"],
            "dettagli": dettagli
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(500, f"Errore caricamento ordine: {str(e)}")

@router.get("/")
def get_active_orders(date: str = None):
    """Ottiene tutti gli ordini attivi con filtro data specifico"""
    conn = get_conn()
    
    try:
        # Costruisci filtro data
        date_filter = ""
        if date:
            # Data specifica (formato YYYY-MM-DD)
            date_filter = f"AND DATE(o.data_ora) = DATE('{date}')"
        else:
            # Default: oggi
            date_filter = "AND DATE(o.data_ora) = DATE('now')"
        
        # Ordini attivi (non completati) con filtro data
        rows = conn.execute(f"""
            SELECT o.id, o.numero_tavolo, o.data_ora, o.stato, o.totale, 
                   COALESCE(o.numero_persone, 1) as numero_persone,
                   COALESCE(o.coperto, 0) as coperto
            FROM ordini o
            WHERE o.stato != 'completato' {date_filter}
            ORDER BY o.data_ora DESC
        """).fetchall()
        
        orders = []
        for row in rows:
            # Dettagli ordine
            det_rows = conn.execute("""
                SELECT od.pizza_id, mi.nome as pizza_nome, od.quantita, od.note, 
                       COALESCE(od.prezzo_personalizzato, od.prezzo_unitario) as prezzo_unitario,
                       od.prezzo_unitario as prezzo_base,
                       (od.quantita * COALESCE(od.prezzo_personalizzato, od.prezzo_unitario)) as subtotale,
                       COALESCE(od.served, 0) as served, od.note_modifiche
                FROM ordine_dettagli od
                JOIN menu_items mi ON od.pizza_id = mi.id
                WHERE od.ordine_id = ?
            """, (row["id"],)).fetchall()
            
            dettagli = [
                {
                    "pizza_id": r["pizza_id"],
                    "pizza_nome": r["pizza_nome"],
                    "quantita": r["quantita"],
                    "note": r["note"],
                    "prezzo_unitario": r["prezzo_unitario"],
                    "prezzo_base": r["prezzo_base"],
                    "subtotale": r["subtotale"],
                    "served": bool(r["served"]),
                    "note_modifiche": r["note_modifiche"]
                }
                for r in det_rows
            ]
            
            orders.append({
                "id": row["id"],
                "numero_tavolo": row["numero_tavolo"],
                "data_ora": row["data_ora"],
                "stato": row["stato"],
                "totale": row["totale"],
                "numero_persone": row["numero_persone"],
                "coperto": row["coperto"],
                "dettagli": dettagli
            })
        
        conn.close()
        return orders
        
    except Exception as e:
        conn.close()
        raise HTTPException(500, f"Errore caricamento ordini attivi: {str(e)}")

@router.patch("/{ordine_id}/items/{item_id}")
def update_item_served(ordine_id: int, item_id: int, data: dict):
    """Aggiorna stato servito di un articolo"""
    conn = get_conn()
    
    try:
        # Verifica esistenza ordine e articolo
        item = conn.execute("""
            SELECT od.id FROM ordine_dettagli od
            WHERE od.ordine_id = ? AND od.pizza_id = ?
        """, (ordine_id, item_id)).fetchone()
        
        if not item:
            raise HTTPException(404, "Articolo non trovato nell'ordine")
        
        # Aggiorna stato servito
        conn.execute("""
            UPDATE ordine_dettagli 
            SET served = ? 
            WHERE ordine_id = ? AND pizza_id = ?
        """, (1 if data.get("served") else 0, ordine_id, item_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "served": data.get("served")}
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(500, f"Errore aggiornamento articolo: {str(e)}")

@router.patch("/{ordine_id}/mark-all-served")
def mark_all_served(ordine_id: int):
    """Segna tutti gli articoli come serviti"""
    conn = get_conn()
    
    try:
        # Verifica esistenza ordine
        order = conn.execute(
            "SELECT id FROM ordini WHERE id = ?", (ordine_id,)
        ).fetchone()
        
        if not order:
            raise HTTPException(404, "Ordine non trovato")
        
        # Aggiorna tutti gli articoli come serviti
        conn.execute("""
            UPDATE ordine_dettagli 
            SET served = 1 
            WHERE ordine_id = ?
        """, (ordine_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True}
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(500, f"Errore aggiornamento ordine: {str(e)}")

@router.patch("/{ordine_id}/complete")
def complete_order(ordine_id: int):
    """Completa un ordine"""
    conn = get_conn()
    
    try:
        # Verifica esistenza ordine
        order = conn.execute(
            "SELECT id FROM ordini WHERE id = ?", (ordine_id,)
        ).fetchone()
        
        if not order:
            raise HTTPException(404, "Ordine non trovato")
        
        # Aggiorna stato ordine
        conn.execute("""
            UPDATE ordini 
            SET stato = 'completato' 
            WHERE id = ?
        """, (ordine_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True}
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(500, f"Errore completamento ordine: {str(e)}")

@router.post("/{ordine_id}/pay")
def process_payment(ordine_id: int, payment_data: dict):
    """Processa il pagamento di un ordine"""
    conn = get_conn()
    
    try:
        # Verifica esistenza ordine e ottieni dettagli
        order = conn.execute("""
            SELECT id, numero_tavolo, totale, stato
            FROM ordini 
            WHERE id = ?
        """, (ordine_id,)).fetchone()
        
        if not order:
            raise HTTPException(404, "Ordine non trovato")
        
        if order["stato"] == "completato":
            raise HTTPException(400, "Ordine gia' completato")
        
        # Verifica metodo pagamento
        metodo = payment_data.get("metodo_pagamento")
        if metodo not in ["carta", "contanti"]:
            raise HTTPException(400, "Metodo pagamento non valido")
        
        importo = payment_data.get("importo", order["totale"])
        
        # Inserisci pagamento
        cursor = conn.execute("""
            INSERT INTO pagamenti (ordine_id, importo, metodo_pagamento, note)
            VALUES (?, ?, ?, ?)
        """, (ordine_id, importo, metodo, payment_data.get("note", "")))
        
        pagamento_id = cursor.lastrowid
        
        # Aggiorna stato ordine a completato
        conn.execute("""
            UPDATE ordini 
            SET stato = 'completato' 
            WHERE id = ?
        """, (ordine_id,))
        
        conn.commit()
        
        # Prepara risposta
        pagamento_info = conn.execute("""
            SELECT id, ordine_id, importo, metodo_pagamento, data_ora, note
            FROM pagamenti 
            WHERE id = ?
        """, (pagamento_id,)).fetchone()
        
        conn.close()
        
        return {
            "success": True,
            "pagamento": {
                "id": pagamento_info["id"],
                "ordine_id": pagamento_info["ordine_id"],
                "importo": pagamento_info["importo"],
                "metodo_pagamento": pagamento_info["metodo_pagamento"],
                "data_ora": pagamento_info["data_ora"],
                "note": pagamento_info["note"]
            },
            "ordine": {
                "id": order["id"],
                "numero_tavolo": order["numero_tavolo"],
                "totale": order["totale"]
            }
        }
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(500, f"Errore processamento pagamento: {str(e)}")

@router.get("/payments/daily")
def get_daily_payments(date: str = None):
    """Ottiene statistiche pagamenti giornalieri"""
    conn = get_conn()
    
    try:
        if date:
            date_filter = f"AND DATE(p.data_ora) = '{date}'"
        else:
            date_filter = "AND DATE(p.data_ora) = DATE('now')"
        
        # Statistiche pagamenti del giorno
        cursor = conn.execute(f"""
            SELECT 
                COUNT(*) as totale_pagamenti,
                SUM(p.importo) as incasso_totale,
                COUNT(CASE WHEN p.metodo_pagamento = 'carta' THEN 1 END) as pagamenti_carta,
                SUM(CASE WHEN p.metodo_pagamento = 'carta' THEN p.importo ELSE 0 END) as incasso_carta,
                COUNT(CASE WHEN p.metodo_pagamento = 'contanti' THEN 1 END) as pagamenti_contanti,
                SUM(CASE WHEN p.metodo_pagamento = 'contanti' THEN p.importo ELSE 0 END) as incasso_contanti
            FROM pagamenti p
            WHERE 1=1 {date_filter}
        """)
        
        stats = cursor.fetchone()
        
        # Ultimi pagamenti
        cursor.execute(f"""
            SELECT p.id, p.importo, p.metodo_pagamento, p.data_ora, o.numero_tavolo
            FROM pagamenti p
            JOIN ordini o ON p.ordine_id = o.id
            WHERE 1=1 {date_filter}
            ORDER BY p.data_ora DESC
            LIMIT 10
        """)
        
        recent_payments = cursor.fetchall()
        
        conn.close()
        
        return {
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'totale_pagamenti': stats['totale_pagamenti'] or 0,
            'incasso_totale': stats['incasso_totale'] or 0,
            'pagamenti_carta': stats['pagamenti_carta'] or 0,
            'incasso_carta': stats['incasso_carta'] or 0,
            'pagamenti_contanti': stats['pagamenti_contanti'] or 0,
            'incasso_contanti': stats['incasso_contanti'] or 0,
            'recent_payments': [
                {
                    'id': row['id'],
                    'importo': row['importo'],
                    'metodo_pagamento': row['metodo_pagamento'],
                    'data_ora': row['data_ora'],
                    'tavolo': row['numero_tavolo']
                }
                for row in recent_payments
            ]
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(500, f"Errore statistiche pagamenti: {str(e)}")

@router.get("/active/{table_number}")
def get_active_order(table_number: int):
    """Controlla se c'è un ordine attivo per un tavolo"""
    conn = get_conn()
    
    try:
        existing_order = conn.execute("""
            SELECT id, numero_tavolo, data_ora, stato, totale, numero_persone
            FROM ordini 
            WHERE numero_tavolo = ? AND stato = 'in_corso'
            ORDER BY data_ora DESC
            LIMIT 1
        """, (table_number,)).fetchone()
        
        if existing_order:
            return {
                "id": existing_order["id"],
                "numero_tavolo": existing_order["numero_tavolo"],
                "data_ora": existing_order["data_ora"],
                "stato": existing_order["stato"],
                "totale": existing_order["totale"],
                "numero_persone": existing_order["numero_persone"]
            }
        else:
            return None
            
    except Exception as e:
        raise HTTPException(500, f"Errore controllo ordine attivo: {str(e)}")
    finally:
        conn.close()

@router.get("/{order_id}/items")
def get_order_items(order_id: int):
    """Ottiene gli item di un ordine"""
    conn = get_conn()
    
    try:
        items = conn.execute("""
            SELECT od.id, od.pizza_id, od.quantita, od.note, od.prezzo_unitario, 
                   od.prezzo_personalizzato, od.note_modifiche,
                   mi.nome as pizza_nome
            FROM ordine_dettagli od
            JOIN menu_items mi ON od.pizza_id = mi.id
            WHERE od.ordine_id = ?
            ORDER BY od.id
        """, (order_id,)).fetchall()
        
        return [
            {
                "id": item["id"],
                "pizza_id": item["pizza_id"],
                "pizza_nome": item["pizza_nome"],
                "quantita": item["quantita"],
                "note": item["note"],
                "prezzo_unitario": item["prezzo_unitario"],
                "prezzo_personalizzato": item["prezzo_personalizzato"],
                "note_modifiche": item["note_modifiche"]
            }
            for item in items
        ]
        
    except Exception as e:
        raise HTTPException(500, f"Errore caricamento item ordine: {str(e)}")
    finally:
        conn.close()

@router.get("/statistics/daily")
def get_daily_statistics(date: str = None):
    """Ottiene statistiche giornaliere"""
    if not PRINT_SERVICE_AVAILABLE:
        raise HTTPException(501, "Servizio statistiche non disponibile")
    
    stats = print_service.get_daily_statistics(date)
    return stats

@router.get("/printer/status")
def get_printer_status():
    """Stato della stampante e coda di stampa"""
    if not PRINT_SERVICE_AVAILABLE:
        return {"status": "unavailable", "queue": []}
    
    return {
        "status": print_service.printer_status.value,
        "bluetooth_connected": print_service.bluetooth_connected,
        "queue_length": len(print_service.print_queue),
        "queue": [
            {
                "order_id": job.order_id,
                "table_number": job.table_number,
                "total": job.total,
                "status": job.status.value,
                "timestamp": job.timestamp.isoformat()
            }
            for job in print_service.print_queue
        ]
    }

@router.post("/printer/test")
def test_printer():
    """Test di stampa - usa console per debug"""
    if not PRINT_SERVICE_AVAILABLE:
        raise HTTPException(501, "Servizio stampa non disponibile")
    
    test_order = {
        'id': 9999,
        'numero_tavolo': 99,
        'totale': 15.50,
        'dettagli': [
            {
                'pizza_nome': 'Pizza Test',
                'quantita': 1,
                'prezzo_unitario': 8.00,
                'subtotale': 8.00,
                'note': 'Test stampa'
            },
            {
                'pizza_nome': 'Coca Cola',
                'quantita': 2,
                'prezzo_unitario': 3.75,
                'subtotale': 7.50,
                'note': ''
            }
        ]
    }
    
    print_job = print_service.add_to_print_queue(test_order)
    success = print_service.print_order_console(print_job)
    
    return {
        "success": success,
        "message": "Test stampa completato" if success else "Errore durante il test"
    }
