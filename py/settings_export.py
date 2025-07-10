import pymysql
import csv

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='db_tms',  # Replace with your actual DB name
)
cursor = conn.cursor()

# Read SQL file
file_path = "settings_queries\settings.txt"
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

# Execute each SELECT query and export to CSV
for idx, query in enumerate(queries):
    if query.lower().startswith("select"):
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        filename = f"settings_export_{idx+1}.csv"
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)  # Write header
            writer.writerows(rows)    # Write data

        print(f"Exported query {idx+1} to {filename}")
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