import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print('📊 DATABASE STRUCTURE CHECK')
print('='*50)

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables found:')
for table in tables:
    print(f'  - {table[0]}')

# Check customer table structure
print('\n🏢 CUSTOMER TABLE STRUCTURE:')
try:
    cursor.execute('PRAGMA table_info(HealthCheck_app_customer)')
    columns = cursor.fetchall()
    monthly_columns = [col[1] for col in columns if 'runs' in col[1] or 'date' in col[1]]
    print('Monthly data columns:')
    for col in monthly_columns:
        print(f'  - {col}')
    
    # Check actual data
    print('\n📅 SAMPLE MONTHLY DATA:')
    cursor.execute('SELECT name, jan_runs, feb_runs, mar_runs, apr_runs, may_runs FROM HealthCheck_app_customer WHERE name IN ("BSNL", "Moratelindo", "Tata") LIMIT 3')
    data = cursor.fetchall()
    for row in data:
        print(f'{row[0]}: Jan={row[1]}, Feb={row[2]}, Mar={row[3]}, Apr={row[4]}, May={row[5]}')
        
except Exception as e:
    print(f'Error checking customer table: {e}')

# Check network table
print('\n🔧 NETWORK TABLE STRUCTURE:')
try:
    cursor.execute('PRAGMA table_info(HealthCheck_app_hcnetwork)')
    columns = cursor.fetchall()
    monthly_columns = [col[1] for col in columns if 'runs' in col[1] or 'date' in col[1]]
    print('Monthly data columns:')
    for col in monthly_columns:
        print(f'  - {col}')
        
    # Check network data
    print('\n📅 SAMPLE NETWORK MONTHLY DATA:')
    cursor.execute('SELECT network_name, jan_runs, feb_runs, mar_runs FROM HealthCheck_app_hcnetwork WHERE customer_id IN (SELECT id FROM HealthCheck_app_customer WHERE name="BSNL") LIMIT 3')
    data = cursor.fetchall()
    for row in data:
        print(f'{row[0]}: Jan={row[1]}, Feb={row[2]}, Mar={row[3]}')
        
except Exception as e:
    print(f'Error checking network table: {e}')

conn.close()