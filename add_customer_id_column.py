import csv

# Read original CSV
input_file = "Dashboard_Export_Enhanced.csv"
output_file = "Dashboard_Export_CloudReady.csv"

print(f"🔧 Adding customer_id column to {input_file}")

with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    
    # Read header
    headers = next(reader)
    
    # Add customer_id as first column
    new_headers = ['customer_id'] + headers
    
    rows = []
    customer_id = 1
    
    for row in reader:
        # Add customer_id to each row
        new_row = [str(customer_id)] + row
        rows.append(new_row)
        customer_id += 1

# Write new CSV
with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(new_headers)
    writer.writerows(rows)

print(f"✅ Created {output_file} with customer_id column")
print(f"📊 Total rows: {len(rows)}")
print("🚀 Upload this file to cloud for import!")