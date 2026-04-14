#!/usr/bin/env python3
import sys
import sqlite3
from db import get_conn

def test_menu_database():
    try:
        conn = get_conn()
        
        # Verifica se le tabelle esistono
        tables = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('menu_items', 'ingredienti', 'menu_item_ingredienti')
        """).fetchall()
        
        print("Tabelle trovate:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Conta menu items
        menu_count = conn.execute("SELECT COUNT(*) as count FROM menu_items WHERE attiva = 1").fetchone()
        print(f"\nMenu items attivi: {menu_count['count']}")
        
        # Mostra tutti i menu items
        items = conn.execute("SELECT * FROM menu_items ORDER BY id").fetchall()
        print("\nTutti i menu items:")
        for item in items:
            print(f"  ID: {item['id']}, Nome: {item['nome']}, Prezzo: €{item['prezzo']}, Categoria: {item['categoria']}, Attiva: {item['attiva']}")
        
        # Conta ingredienti
        ing_count = conn.execute("SELECT COUNT(*) as count FROM ingredienti WHERE attiva = 1").fetchone()
        print(f"\nIngredienti attivi: {ing_count['count']}")
        
        # Mostra tutti gli ingredienti
        ingredienti = conn.execute("SELECT * FROM ingredienti ORDER BY id").fetchall()
        print("\nTutti gli ingredienti:")
        for ing in ingredienti:
            print(f"  ID: {ing['id']}, Nome: {ing['nome']}, Tipo: {ing['tipo']}, Attiva: {ing['attiva']}")
        
        # Conta relazioni
        rel_count = conn.execute("SELECT COUNT(*) as count FROM menu_item_ingredienti").fetchone()
        print(f"\nRelazioni menu-item-ingredienti: {rel_count['count']}")
        
        # Mostra relazioni
        relazioni = conn.execute("""
            SELECT mii.*, mi.nome as menu_nome, i.nome as ing_nome 
            FROM menu_item_ingredienti mii
            JOIN menu_items mi ON mii.menu_item_id = mi.id
            JOIN ingredienti i ON mii.ingrediente_id = i.id
            ORDER BY mii.menu_item_id
        """).fetchall()
        
        print("\nRelazioni menu-item-ingredienti:")
        for rel in relazioni:
            print(f"  Menu: {rel['menu_nome']} -> Ingrediente: {rel['ing_nome']} (Qtà: {rel['quantita']})")
        
        conn.close()
        
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    test_menu_database()
