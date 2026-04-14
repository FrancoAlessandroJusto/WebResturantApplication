
# IMPORT

import sqlite3
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

from core.database import get_conn


# =========================
# ROUTER ANALYTICS API
# =========================

router = APIRouter(prefix="/analytics", tags=["analytics"])


# =========================
# ANALYTICS API
# =========================

@router.get("/summary")
def get_analytics_summary(periodo: str = "today"):
    """Calcola analytics per periodo: today, week, month, year"""
    conn = get_conn()
    
    try:
        # Determina filtro data in base al periodo
        if periodo == "today":
            date_filter = "DATE(o.data_ora) = DATE('now')"
        elif periodo == "week":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-7 days')"
        elif periodo == "month":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-30 days')"
        elif periodo == "year":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-365 days')"
        else:
            date_filter = "DATE(o.data_ora) = DATE('now')"
        
        # Calcola totali ordini
        totals = conn.execute(f"""
            SELECT 
                COUNT(*) as numero_ordini,
                COALESCE(SUM(o.totale), 0) as ricavo_totale
            FROM ordini o
            WHERE o.stato = 'completato' AND {date_filter}
        """).fetchone()
        
        # Calcola vendite per menu item con costi reali
        pizza_query = f"""
            SELECT 
                mi.id as item_id,
                mi.nome as item_nome,
                mi.categoria,
                COALESCE(SUM(od.quantita), 0) as quantita_venduta,
                COALESCE(SUM(od.quantita * od.prezzo_unitario), 0) as ricavo_totale
            FROM menu_items mi
            LEFT JOIN ordine_dettagli od ON mi.id = od.pizza_id
            LEFT JOIN ordini o ON od.ordine_id = o.id
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY mi.id, mi.nome, mi.categoria
            HAVING quantita_venduta > 0
            ORDER BY quantita_venduta DESC
        """
        
        item_data = conn.execute(pizza_query).fetchall()
        
        analytics_data = []
        costo_produzione_totale = 0.0
        
        for row in item_data:
            # Calcola costo reale per questo item
            costo_reale_item = calculate_real_cost(conn, row["item_id"])
            costo_produzione_totale_item = costo_reale_item * row["quantita_venduta"]
            profitto_item = row["ricavo_totale"] - costo_produzione_totale_item
            
            costo_produzione_totale += costo_produzione_totale_item
            
            analytics_data.append({
                "item_id": row["item_id"],
                "item_nome": row["item_nome"],
                "categoria": row["categoria"],
                "quantita_venduta": row["quantita_venduta"],
                "ricavo_totale": row["ricavo_totale"],
                "costo_produzione_totale": costo_produzione_totale_item,
                "costo_unitario": costo_reale_item,
                "profitto": profitto_item,
                "margine_percentuale": (profitto_item / row["ricavo_totale"]) * 100 if row["ricavo_totale"] > 0 else 0
            })
        
        profitto_netto = totals["ricavo_totale"] - costo_produzione_totale
        
        return {
            "periodo": periodo,
            "ricavo_totale": totals["ricavo_totale"],
            "costo_produzione_totale": costo_produzione_totale,
            "profitto_netto": profitto_netto,
            "numero_ordini": totals["numero_ordini"],
            "items_analytics": analytics_data,
            "margine_media": (profitto_netto / totals["ricavo_totale"]) * 100 if totals["ricavo_totale"] > 0 else 0
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(500, f"Errore calcolo analytics: {str(e)}")
    finally:
        conn.close()

def calculate_real_cost(conn, item_id):
    """Calcola il costo reale di un menu item basato sugli ingredienti"""
    try:
        # Prende gli ingredienti del menu item
        ingredients_query = """
            SELECT 
                i.costo_unitario,
                i.quantita_riferimento,
                mii.quantita
            FROM menu_item_ingredienti mii
            JOIN ingredienti i ON mii.ingrediente_id = i.id
            WHERE mii.menu_item_id = ? AND i.attiva = 1
        """
        
        ingredients = conn.execute(ingredients_query, (item_id,)).fetchall()
        
        if not ingredients:
            return 0.0
        
        total_cost = 0.0
        for ing in ingredients:
            # Calcola costo per unità di ingrediente
            costo_per_unita = ing["costo_unitario"] / ing["quantita_riferimento"] if ing["quantita_riferimento"] > 0 else 0
            # Calcola costo totale per questo ingrediente
            total_cost += costo_per_unita * ing["quantita"]
        
        return total_cost
        
    except Exception as e:
        print(f"Errore calcolo costo item {item_id}: {e}")
        return 0.0

@router.get("/trends")
def get_analytics_trends(periodo: str = "month"):
    """Ottiene dati di tendenza per grafici"""
    conn = get_conn()
    
    try:
        # Determina filtro e raggruppamento
        if periodo == "week":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-7 days')"
            group_by = "DATE(o.data_ora)"
        elif periodo == "month":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-30 days')"
            group_by = "DATE(o.data_ora)"
        elif periodo == "year":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-365 days')"
            group_by = "strftime('%Y-%m', o.data_ora)"
        else:
            date_filter = "DATE(o.data_ora) = DATE('now')"
            group_by = "DATE(o.data_ora)"
        
        # Tendenze giornali/mensili
        trends = conn.execute(f"""
            SELECT 
                {group_by} as periodo,
                COUNT(*) as numero_ordini,
                COALESCE(SUM(o.totale), 0) as ricavo_totale,
                AVG(o.totale) as ordine_medio
            FROM ordini o
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY {group_by}
            ORDER BY periodo ASC
        """).fetchall()
        
        # Tendenze per categoria
        category_trends = conn.execute(f"""
            SELECT 
                mi.categoria,
                COUNT(*) as numero_ordini,
                COALESCE(SUM(od.quantita * od.prezzo_unitario), 0) as ricavo_totale
            FROM menu_items mi
            LEFT JOIN ordine_dettagli od ON mi.id = od.pizza_id
            LEFT JOIN ordini o ON od.ordine_id = o.id
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY mi.categoria
            ORDER BY ricavo_totale DESC
        """).fetchall()
        
        # Top 10 items più venduti
        top_items = conn.execute(f"""
            SELECT 
                mi.nome,
                mi.categoria,
                SUM(od.quantita) as quantita_venduta,
                COALESCE(SUM(od.quantita * od.prezzo_unitario), 0) as ricavo_totale
            FROM menu_items mi
            LEFT JOIN ordine_dettagli od ON mi.id = od.pizza_id
            LEFT JOIN ordini o ON od.ordine_id = o.id
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY mi.id, mi.nome, mi.categoria
            HAVING quantita_venduta > 0
            ORDER BY quantita_venduta DESC
            LIMIT 10
        """).fetchall()
        
        conn.close()
        
        return {
            "periodo": periodo,
            "trends": [
                {
                    "periodo": row["periodo"],
                    "numero_ordini": row["numero_ordini"],
                    "ricavo_totale": row["ricavo_totale"],
                    "ordine_medio": row["ordine_medio"]
                }
                for row in trends
            ],
            "category_trends": [
                {
                    "categoria": row["categoria"],
                    "numero_ordini": row["numero_ordini"],
                    "ricavo_totale": row["ricavo_totale"]
                }
                for row in category_trends
            ],
            "top_items": [
                {
                    "nome": row["nome"],
                    "categoria": row["categoria"],
                    "quantita_venduta": row["quantita_venduta"],
                    "ricavo_totale": row["ricavo_totale"]
                }
                for row in top_items
            ]
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(500, f"Errore calcolo tendenze: {str(e)}")
    finally:
        conn.close()

@router.get("/ingredients")
def get_ingredients_analytics(periodo: str = "month"):
    """Analisi consumi ingredienti con costi e trend"""
    conn = get_conn()
    
    try:
        # Determina filtro data
        if periodo == "today":
            date_filter = "DATE(o.data_ora) = DATE('now')"
            prev_date_filter = "DATE(o.data_ora) = DATE('now', '-1 day')"
        elif periodo == "week":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-7 days')"
            prev_date_filter = "DATE(o.data_ora) >= DATE('now', '-14 days') AND DATE(o.data_ora) < DATE('now', '-7 days')"
        elif periodo == "month":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-30 days')"
            prev_date_filter = "DATE(o.data_ora) >= DATE('now', '-60 days') AND DATE(o.data_ora) < DATE('now', '-30 days')"
        elif periodo == "year":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-365 days')"
            prev_date_filter = "DATE(o.data_ora) >= DATE('now', '-730 days') AND DATE(o.data_ora) < DATE('now', '-365 days')"
        else:
            date_filter = "DATE(o.data_ora) = DATE('now')"
            prev_date_filter = "DATE(o.data_ora) = DATE('now', '-1 day')"
        
        # Analisi consumi ingredienti periodo corrente
        current_consumption = conn.execute(f"""
            SELECT 
                i.id,
                i.nome as ingrediente,
                i.costo_unitario,
                i.unita_riferimento,
                i.tipo,
                SUM(mii.quantita * od.quantita) as consumo_quantita,
                (i.costo_unitario / i.quantita_riferimento) * SUM(mii.quantita * od.quantita) as costo_totale,
                COUNT(DISTINCT od.ordine_id) as utilizzi_in_ordini,
                AVG(mii.quantita * od.quantita) as consumo_medio_per_ordine
            FROM ingredienti i
            JOIN menu_item_ingredienti mii ON i.id = mii.ingrediente_id
            JOIN ordine_dettagli od ON mii.menu_item_id = od.pizza_id
            JOIN ordini o ON od.ordine_id = o.id
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY i.id, i.nome, i.costo_unitario, i.unita_riferimento, i.tipo
            HAVING consumo_quantita > 0
            ORDER BY costo_totale DESC
        """).fetchall()
        
        # Analisi consumi periodo precedente per trend
        previous_consumption = conn.execute(f"""
            SELECT 
                i.id,
                SUM(mii.quantita * od.quantita) as consumo_quantita,
                (i.costo_unitario / i.quantita_riferimento) * SUM(mii.quantita * od.quantita) as costo_totale
            FROM ingredienti i
            JOIN menu_item_ingredienti mii ON i.id = mii.ingrediente_id
            JOIN ordine_dettagli od ON mii.menu_item_id = od.pizza_id
            JOIN ordini o ON od.ordine_id = o.id
            WHERE o.stato = 'completato' AND {prev_date_filter}
            GROUP BY i.id
            HAVING consumo_quantita > 0
        """).fetchall()
        
        # Crea dizionario per lookup facile dei dati precedenti
        prev_data = {row['id']: row for row in previous_consumption}
        
        # Calcola trend e prepara dati finali
        ingredients_data = []
        total_cost = 0.0
        total_consumption = 0.0
        
        for row in current_consumption:
            prev_row = prev_data.get(row['id'])
            
            # Calcola trend
            current_cost = row['costo_totale']
            prev_cost = prev_row['costo_totale'] if prev_row else 0
            cost_trend = ((current_cost - prev_cost) / prev_cost * 100) if prev_cost > 0 else 0
            
            current_qty = row['consumo_quantita']
            prev_qty = prev_row['consumo_quantita'] if prev_row else 0
            qty_trend = ((current_qty - prev_qty) / prev_qty * 100) if prev_qty > 0 else 0
            
            # Calcola costo unitario effettivo
            costo_unitario_effettivo = current_cost / current_qty if current_qty > 0 else 0
            
            total_cost += current_cost
            total_consumption += current_qty
            
            ingredients_data.append({
                "id": row['id'],
                "ingrediente": row['ingrediente'],
                "tipo": row['tipo'],
                "costo_unitario": row['costo_unitario'],
                "unita_riferimento": row['unita_riferimento'],
                "consumo_quantita": current_qty,
                "consumo_unitario_display": f"{current_qty:.2f} {row['unita_riferimento']}",
                "costo_totale": current_cost,
                "costo_unitario_effettivo": costo_unitario_effettivo,
                "utilizzi_in_ordini": row['utilizzi_in_ordini'],
                "consumo_medio_per_ordine": row['consumo_medio_per_ordine'],
                "cost_trend_percent": cost_trend,
                "qty_trend_percent": qty_trend,
                "trend_direction": "up" if cost_trend > 5 else "down" if cost_trend < -5 else "stable"
            })
        
        conn.close()
        
        return {
            "periodo": periodo,
            "ingredienti_analytics": ingredients_data,
            "total_cost": total_cost,
            "total_consumption": total_consumption,
            "ingredient_count": len(ingredients_data)
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(500, f"Errore analisi ingredienti: {str(e)}")

@router.get("/alerts")
def get_analytics_alerts(periodo: str = "month"):
    """Genera alert automatici basati su consumi e costi"""
    conn = get_conn()
    
    try:
        # Determina filtro data
        if periodo == "today":
            date_filter = "DATE(o.data_ora) = DATE('now')"
            prev_date_filter = "DATE(o.data_ora) = DATE('now', '-1 day')"
        elif periodo == "week":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-7 days')"
            prev_date_filter = "DATE(o.data_ora) >= DATE('now', '-14 days') AND DATE(o.data_ora) < DATE('now', '-7 days')"
        elif periodo == "month":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-30 days')"
            prev_date_filter = "DATE(o.data_ora) >= DATE('now', '-60 days') AND DATE(o.data_ora) < DATE('now', '-30 days')"
        else:
            date_filter = "DATE(o.data_ora) >= DATE('now', '-30 days')"
            prev_date_filter = "DATE(o.data_ora) >= DATE('now', '-60 days') AND DATE(o.data_ora) < DATE('now', '-30 days')"
        
        alerts = []
        
        # Alert 1: Ingredienti con aumento costo significativo
        cost_increase_alerts = conn.execute(f"""
            SELECT 
                i.nome as ingrediente,
                (i.costo_unitario / i.quantita_riferimento) * SUM(mii.quantita * od.quantita) as current_cost,
                prev.prev_cost,
                ((current_cost - prev.prev_cost) / prev.prev_cost * 100) as increase_percent
            FROM ingredienti i
            JOIN menu_item_ingredienti mii ON i.id = mii.ingrediente_id
            JOIN ordine_dettagli od ON mii.menu_item_id = od.pizza_id
            JOIN ordini o ON od.ordine_id = o.id
            LEFT JOIN (
                SELECT 
                    i2.id,
                    (i2.costo_unitario / i2.quantita_riferimento) * SUM(mii2.quantita * od2.quantita) as prev_cost
                FROM ingredienti i2
                JOIN menu_item_ingredienti mii2 ON i2.id = mii2.ingrediente_id
                JOIN ordine_dettagli od2 ON mii2.menu_item_id = od2.pizza_id
                JOIN ordini o2 ON od2.ordine_id = o2.id
                WHERE o2.stato = 'completato' AND {prev_date_filter}
                GROUP BY i2.id
            ) prev ON i.id = prev.id
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY i.id, i.nome, prev.prev_cost
            HAVING increase_percent > 10 AND current_cost > 50
            ORDER BY increase_percent DESC
        """).fetchall()
        
        for alert in cost_increase_alerts:
            alerts.append({
                "type": "cost_increase",
                "severity": "high" if alert["increase_percent"] > 20 else "medium",
                "title": f"Aumento costo: {alert['ingrediente']}",
                "message": f"Costo aumentato del {alert['increase_percent']:.1f}% rispetto al periodo precedente",
                "value": f"+{alert['increase_percent']:.1f}%",
                "ingrediente": alert["ingrediente"],
                "current_cost": alert["current_cost"],
                "previous_cost": alert["prev_cost"]
            })
        
        # Alert 2: Ingredienti con consumo anomalo (calo significativo)
        consumption_drop_alerts = conn.execute(f"""
            SELECT 
                i.nome as ingrediente,
                SUM(mii.quantita * od.quantita) as current_consumption,
                prev.prev_consumption,
                ((current_consumption - prev.prev_consumption) / prev.prev_consumption * 100) as change_percent
            FROM ingredienti i
            JOIN menu_item_ingredienti mii ON i.id = mii.ingrediente_id
            JOIN ordine_dettagli od ON mii.menu_item_id = od.pizza_id
            JOIN ordini o ON od.ordine_id = o.id
            LEFT JOIN (
                SELECT 
                    i2.id,
                    SUM(mii2.quantita * od2.quantita) as prev_consumption
                FROM ingredienti i2
                JOIN menu_item_ingredienti mii2 ON i2.id = mii2.ingrediente_id
                JOIN ordine_dettagli od2 ON mii2.menu_item_id = od2.pizza_id
                JOIN ordini o2 ON od2.ordine_id = o2.id
                WHERE o2.stato = 'completato' AND {prev_date_filter}
                GROUP BY i2.id
            ) prev ON i.id = prev.id
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY i.id, i.nome, prev.prev_consumption
            HAVING change_percent < -20 AND current_consumption > 0
            ORDER BY change_percent ASC
        """).fetchall()
        
        for alert in consumption_drop_alerts:
            alerts.append({
                "type": "consumption_drop",
                "severity": "medium",
                "title": f"Calo consumo: {alert['ingrediente']}",
                "message": f"Consumo calato del {abs(alert['change_percent']):.1f}% rispetto al periodo precedente",
                "value": f"{alert['change_percent']:.1f}%",
                "ingrediente": alert["ingrediente"],
                "current_consumption": alert["current_consumption"],
                "previous_consumption": alert["prev_consumption"]
            })
        
        # Alert 3: Ingredienti più costosi (top spend)
        top_cost_alerts = conn.execute(f"""
            SELECT 
                i.nome as ingrediente,
                (i.costo_unitario / i.quantita_riferimento) * SUM(mii.quantita * od.quantita) as total_cost,
                SUM(mii.quantita * od.quantita) as consumption
            FROM ingredienti i
            JOIN menu_item_ingredienti mii ON i.id = mii.ingrediente_id
            JOIN ordine_dettagli od ON mii.menu_item_id = od.pizza_id
            JOIN ordini o ON od.ordine_id = o.id
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY i.id, i.nome
            HAVING total_cost > 100
            ORDER BY total_cost DESC
            LIMIT 5
        """).fetchall()
        
        for alert in top_cost_alerts:
            alerts.append({
                "type": "top_cost",
                "severity": "info",
                "title": f"Alto costo: {alert['ingrediente']}",
                "message": f"Spesa totale di €{alert['total_cost']:.2f} per questo ingrediente",
                "value": f"€{alert['total_cost']:.2f}",
                "ingrediente": alert["ingrediente"],
                "total_cost": alert["total_cost"],
                "consumption": alert["consumption"]
            })
        
        conn.close()
        
        return {
            "periodo": periodo,
            "alerts": alerts,
            "total_alerts": len(alerts),
            "severity_breakdown": {
                "high": len([a for a in alerts if a["severity"] == "high"]),
                "medium": len([a for a in alerts if a["severity"] == "medium"]),
                "info": len([a for a in alerts if a["severity"] == "info"])
            }
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(500, f"Errore generazione alert: {str(e)}")

@router.get("/recommendations")
def get_purchase_recommendations(periodo: str = "month"):
    """Genera raccomandazioni per acquisti basati su trend"""
    conn = get_conn()
    
    try:
        # Determina filtro data
        if periodo == "today":
            date_filter = "DATE(o.data_ora) = DATE('now')"
            prev_date_filter = "DATE(o.data_ora) = DATE('now', '-7 days')"
        elif periodo == "week":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-7 days')"
            prev_date_filter = "DATE(o.data_ora) >= DATE('now', '-14 days') AND DATE(o.data_ora) < DATE('now', '-7 days')"
        elif periodo == "month":
            date_filter = "DATE(o.data_ora) >= DATE('now', '-30 days')"
            prev_date_filter = "DATE(o.data_ora) >= DATE('now', '-60 days') AND DATE(o.data_ora) < DATE('now', '-30 days')"
        else:
            date_filter = "DATE(o.data_ora) >= DATE('now', '-30 days')"
            prev_date_filter = "DATE(o.data_ora) >= DATE('now', '-60 days') AND DATE(o.data_ora) < DATE('now', '-30 days')"
        
        recommendations = []
        
        # Raccomandazione 1: Previsione consumi basati su trend
        trend_forecast = conn.execute(f"""
            SELECT 
                i.nome as ingrediente,
                i.unita_riferimento,
                SUM(mii.quantita * od.quantita) as current_consumption,
                prev.prev_consumption,
                CASE 
                    WHEN prev.prev_consumption > 0 
                    THEN (current_consumption - prev.prev_consumption) / prev.prev_consumption
                    ELSE 0 
                END as growth_rate
            FROM ingredienti i
            JOIN menu_item_ingredienti mii ON i.id = mii.ingrediente_id
            JOIN ordine_dettagli od ON mii.menu_item_id = od.pizza_id
            JOIN ordini o ON od.ordine_id = o.id
            LEFT JOIN (
                SELECT 
                    i2.id,
                    SUM(mii2.quantita * od2.quantita) as prev_consumption
                FROM ingredienti i2
                JOIN menu_item_ingredienti mii2 ON i2.id = mii2.ingrediente_id
                JOIN ordine_dettagli od2 ON mii2.menu_item_id = od2.pizza_id
                JOIN ordini o2 ON od2.ordine_id = o2.id
                WHERE o2.stato = 'completato' AND {prev_date_filter}
                GROUP BY i2.id
            ) prev ON i.id = prev.id
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY i.id, i.nome, i.unita_riferimento, prev.prev_consumption
            HAVING current_consumption > 5
            ORDER BY current_consumption DESC
        """).fetchall()
        
        for item in trend_forecast:
            # Previsione per prossimo periodo
            forecast_consumption = item["current_consumption"] * (1 + item["growth_rate"] * 1.5)
            
            recommendations.append({
                "type": "forecast",
                "title": f"Previsione acquisto: {item['ingrediente']}",
                "message": f"Prevedi consumo di {forecast_consumption:.1f} {item['unita_riferimento']} per prossimo periodo",
                "ingrediente": item["ingrediente"],
                "current_consumption": item["current_consumption"],
                "growth_rate": item["growth_rate"],
                "forecast_consumption": forecast_consumption,
                "unita": item["unita_riferimento"],
                "priority": "high" if item["growth_rate"] > 0.1 else "medium"
            })
        
        # Raccomandazione 2: Ingredienti da riordinare urgentemente
        urgent_reorder = conn.execute(f"""
            SELECT 
                i.nome as ingrediente,
                i.unita_riferimento,
                SUM(mii.quantita * od.quantita) as consumption_rate,
                COUNT(DISTINCT od.ordine_id) as order_frequency
            FROM ingredienti i
            JOIN menu_item_ingredienti mii ON i.id = mii.ingrediente_id
            JOIN ordine_dettagli od ON mii.menu_item_id = od.pizza_id
            JOIN ordini o ON od.ordine_id = o.id
            WHERE o.stato = 'completato' AND {date_filter}
            GROUP BY i.id, i.nome, i.unita_riferimento
            HAVING consumption_rate > 10 AND order_frequency > 5
            ORDER BY consumption_rate DESC
            LIMIT 10
        """).fetchall()
        
        for item in urgent_reorder:
            recommendations.append({
                "type": "urgent_reorder",
                "title": f"Riordino urgente: {item['ingrediente']}",
                "message": f"Consumo elevato: {item['consumption_rate']:.1f} {item['unita_riferimento']} in {item['order_frequency']} ordini",
                "ingrediente": item["ingrediente"],
                "consumption_rate": item["consumption_rate"],
                "order_frequency": item["order_frequency"],
                "unita": item["unita_riferimento"],
                "priority": "high"
            })
        
        conn.close()
        
        return {
            "periodo": periodo,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "priority_breakdown": {
                "high": len([r for r in recommendations if r["priority"] == "high"]),
                "medium": len([r for r in recommendations if r["priority"] == "medium"])
            }
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(500, f"Errore raccomandazioni acquisti: {str(e)}")

@router.get("/payments")
def get_analytics_payments(periodo: str = "month"):
    """Analisi pagamenti per periodo"""
    conn = get_conn()
    
    try:
        # Determina filtro data
        if periodo == "today":
            date_filter = "DATE(p.data_ora) = DATE('now')"
        elif periodo == "week":
            date_filter = "DATE(p.data_ora) >= DATE('now', '-7 days')"
        elif periodo == "month":
            date_filter = "DATE(p.data_ora) >= DATE('now', '-30 days')"
        elif periodo == "year":
            date_filter = "DATE(p.data_ora) >= DATE('now', '-365 days')"
        else:
            date_filter = "DATE(p.data_ora) = DATE('now')"
        
        # Statistiche pagamenti
        payment_stats = conn.execute(f"""
            SELECT 
                COUNT(*) as totale_pagamenti,
                SUM(p.importo) as incasso_totale,
                COUNT(CASE WHEN p.metodo_pagamento = 'carta' THEN 1 END) as pagamenti_carta,
                SUM(CASE WHEN p.metodo_pagamento = 'carta' THEN p.importo ELSE 0 END) as incasso_carta,
                COUNT(CASE WHEN p.metodo_pagamento = 'contanti' THEN 1 END) as pagamenti_contanti,
                SUM(CASE WHEN p.metodo_pagamento = 'contanti' THEN p.importo ELSE 0 END) as incasso_contanti
            FROM pagamenti p
            WHERE 1=1 {date_filter}
        """).fetchone()
        
        conn.close()
        
        return {
            "periodo": periodo,
            "totale_pagamenti": payment_stats["totale_pagamenti"] or 0,
            "incasso_totale": payment_stats["incasso_totale"] or 0,
            "pagamenti_carta": payment_stats["pagamenti_carta"] or 0,
            "incasso_carta": payment_stats["incasso_carta"] or 0,
            "pagamenti_contanti": payment_stats["pagamenti_contanti"] or 0,
            "incasso_contanti": payment_stats["incasso_contanti"] or 0,
            "percentuale_carta": (payment_stats["incasso_carta"] or 0) / (payment_stats["incasso_totale"] or 1) * 100,
            "percentuale_contanti": (payment_stats["incasso_contanti"] or 0) / (payment_stats["incasso_totale"] or 1) * 100
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(500, f"Errore analisi pagamenti: {str(e)}")
    finally:
        conn.close()
