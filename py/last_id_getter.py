import pymysql
import csv
import os

# === CONFIGURATION ===
host = "localhost"
user = "root"
password = ""
database = "db_tms_qav"  # Change to your database name
output_folder = "generated_exports"
output_file = "last_ids_per_table.csv"

# Connect to MySQL
conn = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
cursor = conn.cursor()

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, output_file)

# Get list of all tables
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()

# Prepare results
results = []

print("Checking last ID for each table...")
for table in tables:
    table_name = table[0]  # table is returned as a tuple
    try:
        # Query to get MAX(id), assuming the primary key column is named 'id'
        cursor.execute(f"SELECT MAX(id) FROM `{table_name}`;")
        result = cursor.fetchone()
        last_id = result[0] if result[0] is not None else 0  # Handle NULL (empty table)
        results.append({"table_name": table_name, "last_id": last_id})
        # print(f"Table: {table_name} → Last ID: {last_id}")
    except Exception as e:
        print(f"⚠️ Error reading from table '{table_name}': {e}")
        results.append({"table_name": table_name, "last_id": None})

# Write results to CSV
with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["table_name", "last_id"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"\n✅ Results saved to: {output_path}")

# Close connection
cursor.close()
conn.close()