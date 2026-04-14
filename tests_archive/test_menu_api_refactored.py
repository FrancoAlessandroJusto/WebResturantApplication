#!/usr/bin/env python3
"""
Test del menu API dopo refactoring con Database Manager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.api.menu import list_menu_items, get_menu_item
from fastapi import HTTPException

def test_menu_api():
    """Test del menu API refactored"""
    print("Test Menu API Refactored...")
    
    try:
        # Test 1: list_menu_items
        items = list_menu_items()
        print(f"Test 1: list_menu_items OK - {len(items)} items")
        
        # Test 2: get_menu_item (esistente)
        if items:
            first_item = get_menu_item(items[0]['id'])
            print(f"Test 2: get_menu_item OK - {first_item['nome']}")
        
        # Test 3: get_menu_item (non esistente)
        try:
            get_menu_item(99999)
            print("Test 3: get_menu_item (404) FALLITO")
        except HTTPException as e:
            print(f"Test 3: get_menu_item (404) OK - {e.status_code}")
        
        print("Menu API test completato con successo!")
        return True
        
    except Exception as e:
        print(f"Menu API test FALLITO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TEST MENU API REFACTORED")
    print("=" * 50)
    
    if test_menu_api():
        print("SUCCESSO: Menu API refactored funzionante!")
    else:
        print("ERRORE: Menu API refactored non funzionante!")
