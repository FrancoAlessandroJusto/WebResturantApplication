#!/usr/bin/env python3
"""
Script temporaneo per popolare il database con ingredienti e pizze napoletane
"""

import sqlite3
import sys
from pathlib import Path

# Aggiungi la directory del progetto al path
sys.path.append(str(Path(__file__).parent))

def get_db_path():
    """Trova il percorso del database"""
    # Usa lo stesso percorso del db.py
    return "pizzeria.db"

def populate_database():
    """Popola il database con ingredienti e pizze napoletane"""
    
    # Prima inizializza il database
    try:
        from db import init_db
        init_db()
        print("Database inizializzato")
    except Exception as e:
        print(f"Errore nell'inizializzazione del database: {e}")
        return False
    
    db_path = get_db_path()
    print(f"Usando database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ingredienti base per pizze napoletane
        ingredienti = [
            ("Pomodoro San Marzano", "base", 3.50, "kg", 1.0),
            ("Fiordilatte", "formaggio", 8.00, "kg", 1.0),
            ("Parmigiano Reggiano DOP 24 mesi", "formaggio", 25.00, "kg", 1.0),
            ("Basilico Fresco", "verdura", 2.00, "mazzo", 1.0),
            ("Olio d'oliva", "altro", 12.00, "litro", 1.0),
            ("Bufala Campana DOP", "formaggio", 15.00, "kg", 1.0),
            ("Bocconcino di Bufala DOP", "formaggio", 18.00, "kg", 1.0),
            ("Salsiccia Toscano", "carne", 12.00, "kg", 1.0),
            ("Patate", "verdura", 2.50, "kg", 1.0),
            ("Bacon Croccante", "carne", 10.00, "kg", 1.0),
            ("Crocchè di Patate", "altro", 8.00, "kg", 1.0),
            ("Mayo Smoked Bacon", "altro", 6.00, "litro", 1.0),
            ("Stracciatella Pugliese", "formaggio", 14.00, "kg", 1.0),
            ("Pomodorini Datterini Gialli", "verdura", 4.00, "kg", 1.0),
            ("Prosciutto Crudo Parma 18 mesi", "carne", 35.00, "kg", 1.0),
            ("Granella di Pistacchio Bronte", "altro", 45.00, "kg", 1.0),
            ("Wurstel Artigianali", "carne", 8.00, "kg", 1.0),
            ("Patate Dippers", "verdura", 3.00, "kg", 1.0),
            ("Maionese al Pepe", "altro", 5.00, "litro", 1.0),
            ("Cremina di Tartufo", "altro", 25.00, "litro", 1.0),
            ("Zucchine", "verdura", 3.50, "kg", 1.0),
            ("Nduja di Spilinga", "carne", 15.00, "kg", 1.0),
            ("Spianata Calabrese", "carne", 12.00, "kg", 1.0),
            ("Filetti di Acciughe", "carne", 20.00, "kg", 1.0),
            ("Capperi di Salina", "altro", 18.00, "kg", 1.0),
            ("Ricotta di Bufala", "formaggio", 12.00, "kg", 1.0),
            ("Salame Piccante", "carne", 14.00, "kg", 1.0),
            ("Rucola Selvatica", "verdura", 4.00, "mazzo", 1.0),
            ("Pesto di Basilico", "salsa", 8.00, "litro", 1.0),
            ("Mortadella Bologna IGP", "carne", 22.00, "kg", 1.0),
            ("Cremina di Pistacchio", "altro", 30.00, "litro", 1.0),
            ("Funghi Champignons", "verdura", 5.00, "kg", 1.0),
            ("Prosciutto Cotto Fiorucci", "carne", 16.00, "kg", 1.0),
            ("Ortaggi di Stagione", "verdura", 4.00, "kg", 1.0),
            ("Gorgonzola", "formaggio", 10.00, "kg", 1.0),
            ("Grana Padano", "formaggio", 18.00, "kg", 1.0),
            ("Patatine Fritte", "altro", 3.00, "kg", 1.0),
            ("Cremina di Pomodorino Giallo", "altro", 12.00, "litro", 1.0),
            ("Pomodorino Datterino Rosso", "verdura", 5.00, "kg", 1.0),
            ("Burrata Pugliese", "formaggio", 16.00, "kg", 1.0),
            ("Friarielli", "verdura", 6.00, "kg", 1.0)
        ]
        
        # Inserisci ingredienti
        print("Inserimento ingredienti...")
        cursor.executemany("""
            INSERT OR IGNORE INTO ingredienti 
            (nome, tipo, costo_unitario, unita_riferimento, quantita_riferimento) 
            VALUES (?, ?, ?, ?, ?)
        """, ingredienti)
        
        # Pizze napoletane con ingredienti e quantità
        pizze = [
            ("Margherita a ruota di carro", 8.00, "Pizza", [
                ("Pomodoro San Marzano", 0.2),
                ("Fiordilatte", 0.15),
                ("Parmigiano Reggiano DOP 24 mesi", 0.05),
                ("Basilico Fresco", 0.02),
                ("Olio d'oliva", 0.02)
            ]),
            ("NA' MARGHERITA", 12.00, "Pizza", [
                ("Pomodoro San Marzano", 0.25),
                ("Fiordilatte", 0.2),
                ("Parmigiano Reggiano DOP 24 mesi", 0.08),
                ("Basilico Fresco", 0.03),
                ("Olio d'oliva", 0.03)
            ]),
            ("Robin Hood", 12.00, "Pizza", [
                ("Cremina di Tartufo", 0.05),
                ("Fiordilatte", 0.15),
                ("Salsiccia Toscano", 0.1),
                ("Patate", 0.15)
            ]),
            ("La Crokkante", 14.00, "Pizza", [
                ("Fiordilatte", 0.15),
                ("Crocchè di Patate", 0.1),
                ("Bacon Croccante", 0.08),
                ("Salsiccia Toscano", 0.1),
                ("Mayo Smoked Bacon", 0.03)
            ]),
            ("Alleanza", 10.00, "Pizza", [
                ("Fiordilatte", 0.15),
                ("Stracciatella Pugliese", 0.08),
                ("Pomodorini Datterini Gialli", 0.1),
                ("Prosciutto Crudo Parma 18 mesi", 0.08),
                ("Granella di Pistacchio Bronte", 0.03)
            ]),
            ("Na'Scostumata", 15.00, "Pizza", [
                ("Fiordilatte", 0.15),
                ("Wurstel Artigianali", 0.1),
                ("Patate Dippers", 0.15),
                ("Maionese al Pepe", 0.03),
                ("Parmigiano Reggiano DOP 24 mesi", 0.05)
            ]),
            ("La Wallera", 10.50, "Pizza", [
                ("Cremina di Pomodorino Giallo", 0.05),
                ("Fiordilatte", 0.15),
                ("Pomodorino Datterino Rosso", 0.1),
                ("Burrata Pugliese", 0.08),
                ("Grana Padano", 0.05)
            ]),
            ("DIEGO", 10.50, "Pizza", [
                ("Fiordilatte", 0.15),
                ("Salsiccia Toscano", 0.1),
                ("Friarielli", 0.1),
                ("Olio d'oliva", 0.03)
            ]),
            ("BUFALA", 10.00, "Pizza", [
                ("Pomodoro San Marzano", 0.2),
                ("Bufala Campana DOP", 0.2),
                ("Bocconcino di Bufala DOP", 0.05),
                ("Olio d'oliva", 0.03),
                ("Basilico Fresco", 0.02)
            ]),
            ("NAPOLI", 11.00, "Pizza", [
                ("Pomodoro San Marzano", 0.2),
                ("Fiordilatte", 0.15),
                ("Filetti di Acciughe", 0.03),
                ("Capperi di Salina", 0.02),
                ("Olio d'oliva", 0.03)
            ]),
            ("Pizza Fritta", 14.00, "Pizza", [
                ("Ricotta di Bufala", 0.15),
                ("Salame Piccante", 0.08),
                ("Salsiccia Toscano", 0.1)
            ]),
            ("LEBOWSKI", 10.00, "Pizza", [
                ("Fiordilatte", 0.15),
                ("Zucchine", 0.15),
                ("Salsiccia Toscano", 0.1),
                ("Stracciatella Pugliese", 0.08),
                ("Olio d'oliva", 0.03)
            ]),
            ("CARLITO'S WAY", 14.00, "Pizza", [
                ("Pomodoro San Marzano", 0.2),
                ("Fiordilatte", 0.15),
                ("Nduja di Spilinga", 0.05),
                ("Spianata Calabrese", 0.08),
                ("Olio d'oliva", 0.03)
            ]),
            ("Cortigiana", 10.00, "Pizza", [
                ("Fiordilatte", 0.15),
                ("Prosciutto Crudo Parma 18 mesi", 0.08),
                ("Rucola Selvatica", 0.05),
                ("Grana Padano", 0.05),
                ("Bocconcino di Bufala DOP", 0.05)
            ]),
            ("Tricolore", 14.00, "Pizza", [
                ("Pesto di Basilico", 0.05),
                ("Pomodorino Datterino Rosso", 0.15),
                ("Fiordilatte", 0.15)
            ]),
            ("Piazza Dante", 10.00, "Pizza", [
                ("Fiordilatte", 0.15),
                ("Mortadella Bologna IGP", 0.08),
                ("Burrata Pugliese", 0.08),
                ("Cremina di Pistacchio", 0.05),
                ("Granella di Pistacchio Bronte", 0.03)
            ]),
            ("Cotto e Funghi", 9.00, "Pizza", [
                ("Fiordilatte", 0.15),
                ("Funghi Champignons", 0.12),
                ("Prosciutto Cotto Fiorucci", 0.08)
            ]),
            ("Vegetariana", 10.00, "Pizza", [
                ("Pomodoro San Marzano", 0.2),
                ("Fiordilatte", 0.15),
                ("Ortaggi di Stagione", 0.15)
            ]),
            ("DONN'ALFÒ", 10.00, "Pizza", [
                ("Fiordilatte", 0.15),
                ("Salsiccia Toscano", 0.1),
                ("Patate", 0.15)
            ]),
            ("4 Formaggi", 12.00, "Pizza", [
                ("Fiordilatte", 0.1),
                ("Bufala Campana DOP", 0.1),
                ("Gorgonzola", 0.08),
                ("Grana Padano", 0.05)
            ]),
            # Varie
            ("Ciccino", 5.00, "Varie", [
                ("Patatine Fritte", 0.15),
                ("Wurstel Artigianali", 0.08)
            ]),
            ("Zeppole Napoletane", 4.00, "Varie", []),
            ("Carmelina Wrustel", 4.99, "Varie", [
                ("Wurstel Artigianali", 0.1)
            ]),
            ("Carmelina Salsiccia e Provola", 4.99, "Varie", [
                ("Salsiccia Toscano", 0.08),
                ("Fiordilatte", 0.08)
            ]),
            ("Carmelina Pancetta e Pistacchio", 4.99, "Varie", [
                ("Bacon Croccante", 0.08),
                ("Granella di Pistacchio Bronte", 0.02)
            ]),
            ("Frittatina di Pasta", 3.00, "Varie", []),
            ("Fritto della Napoletana 2.0", 15.00, "Varie", []),
            ("Carmelina Classica", 3.50, "Varie", []),
            ("Pastierina Napoletana", 4.00, "Varie", []),
            # Dolci
            ("Tiramisù", 4.00, "Dolci", []),
            ("Angioletti alla nutella", 5.00, "Dolci", [])
        ]
        
        # Inserisci pizze
        print("Inserimento pizze...")
        for nome, prezzo, categoria, ingredienti_lista in pizze:
            # Inserisci la pizza
            cursor.execute("""
                INSERT OR IGNORE INTO menu_items 
                (nome, prezzo, categoria, attiva) 
                VALUES (?, ?, ?, 1)
            """, (nome, prezzo, categoria))
            
            # Ottieni l'ID della pizza
            cursor.execute("SELECT id FROM menu_items WHERE nome = ?", (nome,))
            pizza_id = cursor.fetchone()[0]
            
            # Inserisci gli ingredienti per questa pizza
            for ing_nome, quantita in ingredienti_lista:
                # Trova l'ID dell'ingrediente
                cursor.execute("SELECT id FROM ingredienti WHERE nome = ?", (ing_nome,))
                ing_result = cursor.fetchone()
                
                if ing_result:
                    ing_id = ing_result[0]
                    cursor.execute("""
                        INSERT OR IGNORE INTO menu_item_ingredienti 
                        (menu_item_id, ingrediente_id, quantita) 
                        VALUES (?, ?, ?)
                    """, (pizza_id, ing_id, quantita))
                    print(f"  - {nome}: {ing_nome} ({quantita})")
                else:
                    print(f"  - ATTENZIONE: Ingrediente '{ing_nome}' non trovato per '{nome}'")
        
        conn.commit()
        conn.close()
        
        print("\nDatabase popolato con successo!")
        print(f"Ingredienti inseriti: {len(ingredienti)}")
        print(f"Pizze inserite: {len(pizze)}")
        
        # Statistiche
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ingredienti WHERE attiva = 1")
        ing_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE attiva = 1")
        pizza_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM menu_item_ingredienti")
        rel_count = cursor.fetchone()[0]
        
        print(f"\nStatistiche finali:")
        print(f"   Ingredienti attivi: {ing_count}")
        print(f"   Menu items attivi: {pizza_count}")
        print(f"   Relazioni ingrediente-pizza: {rel_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Errore durante il popolamento: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Popolamento Database Pizzeria Napoletana 2.0")
    print("=" * 50)
    
    success = populate_database()
    
    if success:
        print("\nOperazione completata!")
        print("Ora puoi accedere a: http://127.0.0.1:8000/mgmt/ui")
    else:
        print("\nOperazione fallita!")
        sys.exit(1)
