# IMPORT esenziali per il router API di analytics
import sqlite3
from fastapi import APIRouter, HTTPException

# Import funzione per ottenere connessione al database
from db import get_conn

# ROUTER ANALYTICS API

router = APIRouter(prefix="/analytics", tags=["analytics"])


# =========================
# ANALYTICS API
# =========================

@router.get("/summary")
def get_analytics_summary(periodo: str = "today"):
    """Calcola analytics per periodo: today, week, month"""
    conn = get_conn()
    
    # Determina filtro data in base al periodo
    if periodo == "today":
        date_filter = "date(data_ora) = date('now')"
    elif periodo == "week":
        date_filter = "data_ora >= date('now', '-7 days')"
    elif periodo == "month":
        date_filter = "data_ora >= date('now', '-30 days')"
    else:
        date_filter = "date(data_ora) = date('now')"
    
    # Calcola totali
    totals = conn.execute(f"""
        SELECT 
            COUNT(*) as numero_ordini,
            COALESCE(SUM(totale), 0) as ricavo_totale
        FROM ordini 
        WHERE stato != 'pending' AND {date_filter}
    """).fetchone()
    
    # Calcola vendite per pizza (semplificato senza costi produzione per ora)
    pizza_query = f"""
        SELECT 
            p.id as pizza_id,
            p.nome as pizza_nome,
            COALESCE(SUM(od.quantita), 0) as quantita_venduta,
            COALESCE(SUM(od.quantita * od.prezzo_unitario), 0) as ricavo_totale
        FROM pizze p
        LEFT JOIN ordine_dettagli od ON p.id = od.pizza_id
        LEFT JOIN ordini o ON od.ordine_id = o.id
        WHERE o.stato != 'pending' AND {date_filter}
        GROUP BY p.id, p.nome
        HAVING quantita_venduta > 0
        ORDER BY quantita_venduta DESC
    """
    
    pizza_data = conn.execute(pizza_query).fetchall()
    conn.close()
    
    pizze_analytics = []
    costo_produzione_totale = 0.0  # Semplificato per ora
    
    for row in pizza_data:
        # Stima costo produzione come 60% del ricavo (semplificato)
        costo_produzione_pizza = row["ricavo_totale"] * 0.6
        profitto = row["ricavo_totale"] - costo_produzione_pizza
        costo_produzione_totale += costo_produzione_pizza
        
        pizze_analytics.append({
            "pizza_id": row["pizza_id"],
            "pizza_nome": row["pizza_nome"],
            "quantita_venduta": row["quantita_venduta"],
            "ricavo_totale": row["ricavo_totale"],
            "costo_produzione_totale": costo_produzione_pizza,
            "profitto": profitto
        })
    
    profitto_netto = totals["ricavo_totale"] - costo_produzione_totale
    
    return {
        "periodo": periodo,
        "ricavo_totale": totals["ricavo_totale"],
        "costo_produzione_totale": costo_produzione_totale,
        "profitto_netto": profitto_netto,
        "numero_ordini": totals["numero_ordini"],
        "pizze_analytics": pizze_analytics
    }
