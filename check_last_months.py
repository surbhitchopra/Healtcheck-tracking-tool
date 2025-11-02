import pandas as pd
from datetime import datetime

df = pd.read_excel(r'C:\Users\surchopr\Hc_Final\Script\Health_Check_Tracker_1.xlsx', sheet_name='Summary')
first_row = df.iloc[0]
datetime_cols = [col for col in df.columns if isinstance(col, datetime)]

print("=== LAST 6 MONTHS DATA ===")
print(f"Customer: {first_row['Customer']} - {first_row['Network']}")

# Check last 6 datetime columns
last_6_cols = datetime_cols[-6:]
for col in last_6_cols:
    value = first_row[col]
    has_data = pd.notna(value) and str(value).strip() != '' and str(value).lower() != 'nan'
    print(f"{col.strftime('%b %Y')}: {'HAS DATA' if has_data else 'NO DATA'} - Value: {value}")

print("\n=== ALL MONTHS DATA ===")
for col in datetime_cols:
    value = first_row[col]
    has_data = pd.notna(value) and str(value).strip() != '' and str(value).lower() != 'nan'
    print(f"{col.strftime('%b %Y')}: {'✅' if has_data else '❌'} - {value}")