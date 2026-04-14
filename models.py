from dataclasses import dataclass, field
from typing import List, Optional
import sqlite3
from core.database import get_conn

@dataclass
class Ingrediente:
    """Classe per rappresentare un ingrediente"""
    id: int = field(default=None)
    nome: str = field(default=None)
    tipo: str = 'altro'
    costo_unitario: float = 0.0
    unita_riferimento: str = 'pz'
    quantita_riferimento: float = 1.0
    attiva: bool = True
    
    @classmethod
    def from_db(cls, row: sqlite3.Row) -> 'Ingrediente':
        """Crea oggetto Ingrediente da riga database"""
        # Accesso sicuro alle colonne con dict()
        row_dict = dict(row)
        
        return cls(
            id=row_dict.get('id', 0),
            nome=row_dict.get('nome', ''),
            tipo=row_dict.get('tipo', 'altro'),
            costo_unitario=row_dict.get('costo_unitario', 0.0),
            unita_riferimento=row_dict.get('unita_riferimento', 'pz'),
            quantita_riferimento=row_dict.get('quantita_riferimento', 1.0),
            attiva=bool(row_dict.get('attiva', 1))
        )
    
    @classmethod
    def get_all(cls) -> List['Ingrediente']:
        """Ottieni tutti gli ingredienti attivi"""
        conn = get_conn()
        rows = conn.execute(
            "SELECT * FROM ingredienti WHERE attiva = 1 ORDER BY nome"
        ).fetchall()
        conn.close()
        return [cls.from_db(row) for row in rows]
    
    @classmethod
    def create(cls, nome: str, tipo: str = 'altro', costo_unitario: float = 0.0, unita_riferimento: str = 'pz', quantita_riferimento: float = 1.0) -> 'Ingrediente':
        """Crea nuovo ingrediente nel database"""
        conn = get_conn()
        cursor = conn.execute(
            "INSERT INTO ingredienti (nome, tipo, costo_unitario, unita_riferimento, quantita_riferimento) VALUES (?, ?, ?, ?, ?)",
            (nome, tipo, costo_unitario, unita_riferimento, quantita_riferimento)
        )
        conn.commit()
        ing_id = cursor.lastrowid
        conn.close()
        
        return cls(
            id=ing_id,
            nome=nome,
            tipo=tipo,
            costo_unitario=costo_unitario,
            unita_riferimento=unita_riferimento,
            quantita_riferimento=quantita_riferimento
        )
    
    def to_dict(self) -> dict:
        """Converte in dizionario per API"""
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'costo_unitario': self.costo_unitario,
            'unita_riferimento': self.unita_riferimento,
            'quantita_riferimento': self.quantita_riferimento
        }


@dataclass
class IngredienteQuantita:
    """Classe per rappresentare un ingrediente con quantità in un menu item"""
    ingrediente: Ingrediente
    quantita: float
    
    def to_dict(self) -> dict:
        """Converte in dizionario per template"""
        return {
            'nome': self.ingrediente.nome,
            'quantita': self.quantita,
            'unita_riferimento': self.ingrediente.unita_riferimento,
            'costo_unitario': self.ingrediente.costo_unitario,
            'quantita_riferimento': self.ingrediente.quantita_riferimento,
            'ingrediente': {
                'nome': self.ingrediente.nome,
                'costo_unitario': self.ingrediente.costo_unitario,
                'quantita_riferimento': self.ingrediente.quantita_riferimento,
                'unita_riferimento': self.ingrediente.unita_riferimento
            }
        }


@dataclass
class MenuItem:
    """Classe per rappresentare un item del menu (pizza, bevanda, etc.)"""
    id: int = field(default=None)
    nome: str = field(default=None)
    prezzo: float = 0.0
    categoria: str = field(default=None)
    attiva: bool = True
    ingredienti: List[IngredienteQuantita] = field(default_factory=list)
    
    @classmethod
    def from_db(cls, row: sqlite3.Row, ingredienti: List[IngredienteQuantita] = None) -> 'MenuItem':
        """Crea oggetto MenuItem da riga database"""
        # Accesso sicuro alle colonne con dict()
        row_dict = dict(row)
        
        return cls(
            id=row_dict.get('id', 0),
            nome=row_dict.get('nome', ''),
            prezzo=row_dict.get('prezzo', 0.0),
            categoria=row_dict.get('categoria', ''),
            attiva=bool(row_dict.get('attiva', 1)),
            ingredienti=ingredienti or []
        )
    
    @classmethod
    def get_all(cls) -> List['MenuItem']:
        """Ottieni tutti i menu items attivi con ingredienti"""
        conn = get_conn()
        
        # Prende tutti i menu items
        items_rows = conn.execute(
            "SELECT * FROM menu_items WHERE attiva = 1 ORDER BY categoria, nome"
        ).fetchall()
        
        items = []
        for item_row in items_rows:
            # Prende gli ingredienti per questo item
            ing_rows = conn.execute("""
                SELECT i.*, mii.quantita
                FROM ingredienti i
                JOIN menu_item_ingredienti mii ON i.id = mii.ingrediente_id
                WHERE mii.menu_item_id = ? AND i.attiva = 1
                ORDER BY i.nome
            """, (item_row['id'],)).fetchall()
            
            # Crea oggetti IngredienteQuantita
            ingredienti = []
            for ing_row in ing_rows:
                ingrediente = Ingrediente.from_db(ing_row)
                quantita = ing_row['quantita']
                ingredienti.append(IngredienteQuantita(ingrediente, quantita))
            
            items.append(cls.from_db(item_row, ingredienti))
        
        conn.close()
        return items
    
    @classmethod
    def create(cls, nome: str, prezzo: float, categoria: str, 
                ingredienti_selezionati: List[dict]) -> 'MenuItem':
        """Crea nuovo menu item con ingredienti"""
        conn = get_conn()
        
        try:
            # Inserisce il menu item
            cursor = conn.execute(
                "INSERT INTO menu_items (nome, prezzo, categoria) VALUES (?, ?, ?)",
                (nome, prezzo, categoria)
            )
            item_id = cursor.lastrowid
            
            # Inserisce gli ingredienti
            for ing_sel in ingredienti_selezionati:
                conn.execute(
                    "INSERT INTO menu_item_ingredienti (menu_item_id, ingrediente_id, quantita) VALUES (?, ?, ?)",
                    (item_id, ing_sel['ingrediente_id'], ing_sel['quantita'])
                )
            
            conn.commit()
            
            # Crea oggetto MenuItem completo con dati reali degli ingredienti
            ingredienti_completi = []
            for ing_sel in ingredienti_selezionati:
                # Carica l'ingrediente dal database per avere dati completi
                ing_row = conn.execute(
                    "SELECT * FROM ingredienti WHERE id = ?", (ing_sel['ingrediente_id'],)
                ).fetchone()
                
                if ing_row:
                    ingrediente = Ingrediente.from_db(ing_row)
                    ingredienti_completi.append(IngredienteQuantita(ingrediente, ing_sel['quantita']))
            
            return cls(
                id=item_id,
                nome=nome,
                prezzo=prezzo,
                categoria=categoria,
                ingredienti=ingredienti_completi
            )
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def to_dict(self) -> dict:
        """Converte in dizionario per API"""
        # Calcola costo totale ingredienti
        costo_ingredienti = 0.0
        for ing in self.ingredienti:
            # Calcola costo per questo ingrediente: (costo_unitario / quantita_riferimento) * quantita
            costo_unitario_reale = ing.ingrediente.costo_unitario / ing.ingrediente.quantita_riferimento if ing.ingrediente.quantita_riferimento > 0 else 0
            costo_ingredienti += costo_unitario_reale * ing.quantita
        
        return {
            'id': self.id,
            'nome': self.nome,
            'prezzo': self.prezzo,
            'categoria': self.categoria,
            'ingredienti': [ing.to_dict() for ing in self.ingredienti],
            'costo_ingredienti': costo_ingredienti
        }
    
    def get_ingredienti_string(self) -> str:
        """Rappresentazione testuale degli ingredienti"""
        if not self.ingredienti:
            return "Nessun ingrediente"
        
        return " • ".join([
            f"{ing.ingrediente.nome} ({ing.quantita}{ing.ingrediente.unita_riferimento})"
            for ing in self.ingredienti
        ])
