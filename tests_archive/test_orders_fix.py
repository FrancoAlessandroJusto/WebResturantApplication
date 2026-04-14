#!/usr/bin/env python3
"""
Test per verificare che le correzioni JavaScript funzionino
"""

import os
import re

def check_orders_js_fixes():
    """Verifica le correzioni JavaScript in orders.html"""
    print("Verifica correzioni JavaScript in orders.html...")
    
    orders_path = "templates/orders.html"
    with open(orders_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues_found = []
    
    # 1. Verifica parseFloat in updateOrderTotal
    if 'parseFloat(item.price) * parseInt(item.quantity)' in content:
        print("OK: Correzione parseFloat applicata in updateOrderTotal")
    else:
        issues_found.append("parseFloat non applicato in updateOrderTotal")
    
    # 2. Verifica parseFloat(orderSubtotal)
    if 'orderSubtotal = parseFloat(orderSubtotal) || 0' in content:
        print("OK: Correzione parseFloat(orderSubtotal) applicata")
    else:
        issues_found.append("parseFloat(orderSubtotal) non applicato")
    
    # 3. Verifica che non ci siano .toFixed su variabili non numeriche
    tofixed_matches = re.findall(r'(\w+)\.toFixed\(', content)
    unsafe_tofixed = []
    for match in tofixed_matches:
        # Controlla se la variabile è convertita in numero prima di .toFixed
        context_start = content.find(match)
        context_end = content.find('.toFixed(', context_start)
        context = content[max(0, context_start-100):context_end]
        
        if 'parseFloat(' not in context and 'parseInt(' not in context and match not in ['orderSubtotal', 'coverCharge', 'totalWithCover']:
            unsafe_tofixed.append(match)
    
    if not unsafe_tofixed:
        print("OK: Nessun .toFixed unsafe trovato")
    else:
        issues_found.append(f".toFixed unsafe su: {unsafe_tofixed}")
    
    return issues_found

def check_base_js_fallback():
    """Verifica il fallback JavaScript in base.html"""
    print("Verifica fallback JavaScript in base.html...")
    
    base_path = "templates/base.html"
    with open(base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues_found = []
    
    # 1. Verifica controllo UIHelper
    if 'typeof UIHelper !== \'undefined\'' in content:
        print("OK: Controllo UIHelper applicato")
    else:
        issues_found.append("Controllo UIHelper non applicato")
    
    # 2. Verifica fallback showMessage
    if 'UIHelper not available, using fallback showMessage' in content:
        print("OK: Fallback showMessage applicato")
    else:
        issues_found.append("Fallback showMessage non applicato")
    
    # 3. Verifica common.js caricato
    if 'common.js' in content:
        print("OK: common.js caricato")
    else:
        issues_found.append("common.js non caricato")
    
    return issues_found

def main():
    print("TEST CORREZIONI JAVASCRIPT")
    print("=" * 40)
    
    # Test orders.html
    orders_issues = check_orders_js_fixes()
    
    print()
    
    # Test base.html
    base_issues = check_base_js_fallback()
    
    print("\n" + "=" * 50)
    print("RIEPILOGO CORREZIONI")
    print("=" * 50)
    
    if not orders_issues and not base_issues:
        print("SUCCESSO: Tutte le correzioni applicate correttamente!")
        print("  - parseFloat applicato in updateOrderTotal")
        print("  - Controllo UIHelper con fallback")
        print("  - Fallback showMessage implementato")
        return True
    else:
        print("ATTENZIONE: Problemi rimasti:")
        for issue in orders_issues:
            print(f"  - orders.html: {issue}")
        for issue in base_issues:
            print(f"  - base.html: {issue}")
        return False

if __name__ == "__main__":
    main()
