"""
Servizio di stampa per ordini - Architettura modulare per Bluetooth e statistiche
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class PrinterStatus(Enum):
    """Stati della stampante"""
    READY = "ready"
    PRINTING = "printing"
    ERROR = "error"
    DISCONNECTED = "disconnected"

class OrderStatus(Enum):
    """Stati ordine"""
    PENDING = "pending"
    PRINTING = "printing"
    PRINTED = "printed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class PrintJob:
    """Job di stampa per ordine"""
    order_id: int
    table_number: int
    items: List[Dict]
    total: float
    timestamp: datetime
    status: OrderStatus = OrderStatus.PENDING
    print_data: Optional[str] = None

class PrintService:
    """Servizio di stampa per ordini - Supporta Bluetooth e statistiche"""
    
    def __init__(self):
        self.printer_status = PrinterStatus.DISCONNECTED
        self.print_queue: List[PrintJob] = []
        self.bluetooth_connected = False
        
    def prepare_print_data(self, order_data: Dict) -> str:
        """
        Prepara i dati di stampa per l'ordine
        Formato compatibile con stampanti termiche POS
        """
        lines = []
        
        # Header
        lines.append("=" * 42)
        lines.append("   PIZZERIA NAPOLITANA 2.0".center(42))
        lines.append("      Via del Gusto, 123 - Siena".center(42))
        lines.append("         Tel: 0577-123456".center(42))
        lines.append("=" * 42)
        lines.append("")
        
        # Info ordine
        order_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        lines.append(f"ORDINE #{order_data['id']:04d}".ljust(20) + f"{order_time}".rjust(22))
        lines.append(f"TAVOLO: {order_data['numero_tavolo']}".center(42))
        lines.append("-" * 42)
        lines.append("")
        
        # Articoli
        lines.append("ARTICOLI".center(42))
        lines.append("-" * 42)
        
        for item in order_data['dettagli']:
            # Nome articolo
            name = item['pizza_nome'].upper()
            if len(name) > 30:
                name = name[:30] + "..."
            
            lines.append(f"{name}".ljust(32))
            
            # Quantità e prezzo
            qty_price = f"{item['quantita']:2d} x {item['prezzo_unitario']:6.2f}".rjust(10)
            lines.append(f"{qty_price}".rjust(42))
            
            # Subtotale
            subtotal = f"{item['subtotale']:7.2f}".rjust(42)
            lines.append(f"{subtotal}".rjust(42))
            
            # Note
            if item.get('note'):
                note = f"  Note: {item['note']}"
                if len(note) > 40:
                    note = note[:40] + "..."
                lines.append(note)
            
            lines.append("")
        
        # Totali
        lines.append("-" * 42)
        lines.append(f"TOTALE:".ljust(32) + f"{order_data['totale']:7.2f}".rjust(10))
        lines.append("=" * 42)
        lines.append("")
        
        # Footer
        lines.append("Grazie per aver scelto".center(42))
        lines.append("Pizzeria Napoletana 2.0!".center(42))
        lines.append("")
        lines.append("=" * 42)
        
        return "\n".join(lines)
    
    def add_to_print_queue(self, order_data: Dict) -> PrintJob:
        """
        Aggiunge ordine alla coda di stampa
        """
        print_job = PrintJob(
            order_id=order_data['id'],
            table_number=order_data['numero_tavolo'],
            items=order_data['dettagli'],
            total=order_data['totale'],
            timestamp=datetime.now(),
            print_data=self.prepare_print_data(order_data)
        )
        
        self.print_queue.append(print_job)
        return print_job
    
    async def print_order_bluetooth(self, print_job: PrintJob) -> bool:
        """
        Stampa ordine via Bluetooth (implementazione futura)
        """
        if not self.bluetooth_connected:
            print("Bluetooth non connesso")
            return False
        
        try:
            # TODO: Implementare connessione Bluetooth e stampa
            # Esempio di implementazione futura:
            # import bluetooth
            # printer_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            # printer_socket.connect((printer_mac_address, 1))
            # printer_socket.send(print_job.print_data.encode('utf-8'))
            # printer_socket.close()
            
            print(f"Stampa ordine #{print_job.order_id} via Bluetooth")
            print_job.status = OrderStatus.PRINTED
            return True
            
        except Exception as e:
            print(f"Errore stampa Bluetooth: {e}")
            print_job.status = OrderStatus.PENDING
            return False
    
    def print_order_console(self, print_job: PrintJob) -> bool:
        """
        Stampa ordine su console (debug/fallback)
        """
        try:
            print("\n" + "="*50)
            print("STAMPA ORDINE (CONSOLE)")
            print("="*50)
            print(print_job.print_data)
            print("="*50)
            print_job.status = OrderStatus.PRINTED
            return True
        except Exception as e:
            print(f"Errore stampa console: {e}")
            return False
    
    async def process_print_queue(self) -> List[bool]:
        """
        Processa tutta la coda di stampa
        """
        results = []
        
        for print_job in self.print_queue:
            if print_job.status == OrderStatus.PENDING:
                print_job.status = OrderStatus.PRINTING
                
                # Prova Bluetooth, fallback su console
                if self.bluetooth_connected:
                    result = await self.print_order_bluetooth(print_job)
                else:
                    result = self.print_order_console(print_job)
                
                results.append(result)
        
        # Rimuovi job completati dalla coda
        self.print_queue = [job for job in self.print_queue if job.status != OrderStatus.PRINTED]
        
        return results
    
    def save_to_statistics(self, order_data: Dict) -> bool:
        """
        Salva dati ordine per statistiche future
        """
        try:
            conn = sqlite3.connect('pizzeria.db')
            cursor = conn.cursor()
            
            # Crea tabella statistiche se non esiste
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    table_number INTEGER NOT NULL,
                    total REAL NOT NULL,
                    items_count INTEGER NOT NULL,
                    category_breakdown TEXT,  -- JSON con conteggio per categoria
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    printed BOOLEAN DEFAULT 0,
                    FOREIGN KEY (order_id) REFERENCES ordini(id)
                )
            """)
            
            # Calcola statistiche
            items_count = len(order_data['dettagli'])
            category_breakdown = {}
            
            # TODO: Aggiungere categoria dei menu items quando disponibili
            # Per ora conta solo gli articoli
            for item in order_data['dettagli']:
                category_breakdown['unknown'] = category_breakdown.get('unknown', 0) + item['quantita']
            
            # Inserisci statistiche
            cursor.execute("""
                INSERT INTO order_statistics 
                (order_id, table_number, total, items_count, category_breakdown)
                VALUES (?, ?, ?, ?, ?)
            """, (
                order_data['id'],
                order_data['numero_tavolo'],
                order_data['totale'],
                items_count,
                json.dumps(category_breakdown)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Errore salvataggio statistiche: {e}")
            return False
    
    def get_daily_statistics(self, date: str = None) -> Dict:
        """
        Ottiene statistiche giornaliere
        """
        try:
            conn = sqlite3.connect('pizzeria.db')
            cursor = conn.cursor()
            
            if date:
                date_filter = f"AND DATE(timestamp) = '{date}'"
            else:
                date_filter = "AND DATE(timestamp) = DATE('now')"
            
            # Statistiche del giorno
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as orders_count,
                    SUM(total) as total_revenue,
                    SUM(items_count) as total_items,
                    AVG(total) as avg_order_value
                FROM order_statistics 
                WHERE 1=1 {date_filter}
            """)
            
            stats = cursor.fetchone()
            
            # Top tavoli
            cursor.execute(f"""
                SELECT table_number, COUNT(*) as orders, SUM(total) as revenue
                FROM order_statistics 
                WHERE 1=1 {date_filter}
                GROUP BY table_number
                ORDER BY revenue DESC
                LIMIT 5
            """)
            
            top_tables = cursor.fetchall()
            
            conn.close()
            
            return {
                'date': date or datetime.now().strftime('%Y-%m-%d'),
                'orders_count': stats['orders_count'] or 0,
                'total_revenue': stats['total_revenue'] or 0,
                'total_items': stats['total_items'] or 0,
                'avg_order_value': stats['avg_order_value'] or 0,
                'top_tables': [
                    {
                        'table': row['table_number'],
                        'orders': row['orders'],
                        'revenue': row['revenue']
                    }
                    for row in top_tables
                ]
            }
            
        except Exception as e:
            print(f"Errore statistiche giornaliere: {e}")
            return {}

# Istanza globale del servizio
print_service = PrintService()
