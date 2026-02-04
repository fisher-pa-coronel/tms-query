import csv

# Option 1: Read from a file (replace 'last_id.csv' with your filename)
last_id = {}
with open('generated_exports/last_ids_per_table.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 0:
            continue  # skip empty rows
        name = row[0].strip()
        value_str = row[1].strip() if len(row) > 1 else ''
        # Convert to int, default to 0 if empty or invalid
        try:
            value = int(value_str) if value_str else 0
        except ValueError:
            value = 0  # fallback for non-integer strings
        last_id[name] = value

print(last_id['clientofferfile'])