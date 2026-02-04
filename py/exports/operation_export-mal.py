import pymysql
import csv
import os
import re  # for regex

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='db_tms_mal',  # Replace with your actual DB name
)
cursor = conn.cursor()

# Define output folder
output_folder = "generated_exports"
os.makedirs(output_folder, exist_ok=True)  # Create if not exists

# Read SQL file
file_path = "ops_queries\\tms-ops-mal.txt"  # Use double backslash or raw string
with open(file_path, 'r') as file:
    content = file.read()

# Parse queries (handle multi-line and ignore comments)
queries = []
current_query = ""
for line in content.splitlines():
    line = line.strip()
    if line.startswith("//") or not line:
        continue
    current_query += " " + line
    if line.endswith(";"):
        queries.append(current_query.strip(";").strip())
        current_query = ""

if current_query.strip():
    queries.append(current_query.strip())

# Function to extract alias from FROM ... AS alias
def get_table_alias(sql):
    match = re.search(r'FROM\s+\w+\s+AS\s+(\w+)', sql, re.IGNORECASE)
    return match.group(1) if match else None

# Execute each SELECT query and export to CSV using alias as filename
for idx, query in enumerate(queries):
    if query.lower().startswith("select"):
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Try to extract table alias
        alias = get_table_alias(query)
        if alias:
            filename = f"{alias}.csv"
        else:
            filename = f"settings_export_{idx+1}.csv"

        file_path_csv = os.path.join(output_folder, filename)

        with open(file_path_csv, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # writer.writerow(columns)  # Write header
            writer.writerows(rows)    # Write data

        print(f"Exported query {idx+1} to '{file_path_csv}'")
    else:
        # Optional: execute non-SELECT queries
        try:
            cursor.execute(query)
            conn.commit()
            print(f"Executed non-SELECT query {idx+1}")
        except Exception as e:
            print(f"⚠️ Error executing query {idx+1}: {e}")

cursor.close()
conn.close()