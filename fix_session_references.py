import csv

# Fix CSV by removing session_id column or setting to NULL
input_file = "Dashboard_Export_CloudReady.csv"
output_file = "Dashboard_Export_NoSessions.csv"

print(f"🔧 Fixing session references in {input_file}")

with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    headers = next(reader)
    
    print(f"📋 Original headers: {headers}")
    
    # Find session-related columns
    session_columns = []
    for i, header in enumerate(headers):
        if 'session' in header.lower():
            session_columns.append(i)
            print(f"🎯 Found session column at index {i}: {header}")
    
    rows = []
    for row in reader:
        # Set session columns to empty/NULL
        for col_idx in session_columns:
            if col_idx < len(row):
                row[col_idx] = ""  # Set to empty string (NULL equivalent)
        rows.append(row)

# Write fixed CSV
with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"✅ Fixed CSV saved as: {output_file}")
print(f"🔧 Session references removed from {len(rows)} rows")
print("🚀 Upload this file to cloud instead!")