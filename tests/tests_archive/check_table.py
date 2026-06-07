import sqlite3

conn = sqlite3.connect('pizzeria.db')
cursor = conn.cursor()

# Ottieni SQL completo della tabella ordini
cursor.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="ordini"')
table_sql = cursor.fetchone()
print('SQL tabella ordini:')
print(table_sql[0] if table_sql else 'Tabella non trovata')

conn.close()
