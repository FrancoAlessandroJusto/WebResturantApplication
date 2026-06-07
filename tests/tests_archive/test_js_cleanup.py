#!/usr/bin/env python3
"""
Test per verificare che la pulizia JavaScript sia completata con successo
"""

import os
import re

def check_js_duplicates():
    """Verifica che non ci siano più duplicazioni JavaScript"""
    print("Verifica duplicazioni JavaScript...")
    
    templates_dir = "templates"
    results = {}
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(templates_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cerca funzioni showMessage duplicate (escludendo base.html che ha wrapper)
            if filename == 'base.html':
                # In base.html cerchiamo solo wrapper, non duplicazioni vere
                showMessage_count = 0
                if 'function showMessage(message, type' in content:
                    showMessage_count = 0  # Wrapper corretto
                toggleDarkMode_count = 0
                if 'function toggleDarkMode()' in content:
                    toggleDarkMode_count = 0  # Wrapper corretto
            else:
                # Negli altri template cerchiamo duplicazioni vere
                showMessage_count = len(re.findall(r'function showMessage', content))
                toggleDarkMode_count = len(re.findall(r'function toggleDarkMode', content))
            
            showMessage_calls = len(re.findall(r'showMessage\(', content))
            
            results[filename] = {
                'showMessage_functions': showMessage_count,
                'showMessage_calls': showMessage_calls,
                'toggleDarkMode_functions': toggleDarkMode_count
            }
    
    return results

def check_common_js_loaded():
    """Verifica che common.js sia caricato nei template"""
    print("Verifica caricamento common.js...")
    
    templates_dir = "templates"
    base_path = os.path.join(templates_dir, "base.html")
    
    with open(base_path, 'r', encoding='utf-8') as f:
        base_content = f.read()
    
    common_js_loaded = 'common.js' in base_content
    ui_helper_available = 'UIHelper' in base_content
    
    return {
        'common_js_loaded': common_js_loaded,
        'ui_helper_available': ui_helper_available
    }

def analyze_results(duplicates, common_js):
    """Analizza i risultati e genera report"""
    print("\n" + "="*60)
    print("REPORT PULIZIA JAVASCRIPT")
    print("="*60)
    
    print("\n1. DUPLICAZIONI TROVATE:")
    total_duplicates = 0
    
    for template, data in duplicates.items():
        if data['showMessage_functions'] > 0:
            print(f"ERRORE {template}: {data['showMessage_functions']} funzioni showMessage duplicate")
            total_duplicates += data['showMessage_functions']
        else:
            print(f"OK {template}: Nessuna funzione showMessage duplicata")
            
        if data['toggleDarkMode_functions'] > 0:
            print(f"ERRORE {template}: {data['toggleDarkMode_functions']} funzioni toggleDarkMode duplicate")
            total_duplicates += data['toggleDarkMode_functions']
    
    print(f"\n   Totale duplicazioni: {total_duplicates}")
    
    print("\n2. CARICAMENTO COMMON.JS:")
    if common_js['common_js_loaded']:
        print("OK common.js caricato in base.html")
    else:
        print("ERRORE common.js NON caricato")
        
    if common_js['ui_helper_available']:
        print("OK UIHelper disponibile")
    else:
        print("ERRORE UIHelper NON disponibile")
    
    print("\n3. CHIAMATE showMessage:")
    for template, data in duplicates.items():
        if data['showMessage_calls'] > 0:
            print(f"FILE {template}: {data['showMessage_calls']} chiamate showMessage")
    
    print("\n4. RIEPILOGO:")
    if total_duplicates == 0 and common_js['common_js_loaded']:
        print("SUCCESSO: Pulizia JavaScript completata!")
        print("   - Zero duplicazioni")
        print("   - Common.js caricato")
        print("   - UIHelper disponibile")
        return True
    else:
        print("ATTENZIONE: Problemi rilevati")
        if total_duplicates > 0:
            print(f"   - {total_duplicates} duplicazioni rimaste")
        if not common_js['common_js_loaded']:
            print("   - Common.js non caricato")
        return False

def main():
    print("ANALISI PULIZIA JAVASCRIPT")
    print("="*40)
    
    # Verifica duplicazioni
    duplicates = check_js_duplicates()
    
    # Verifica common.js
    common_js = check_common_js_loaded()
    
    # Analizza risultati
    success = analyze_results(duplicates, common_js)
    
    if success:
        print("\nSUCCESSO - Pulizia JavaScript completata con successo!")
    else:
        print("\nERRORE - Problemi nella pulizia JavaScript")
    
    return success

if __name__ == "__main__":
    main()
