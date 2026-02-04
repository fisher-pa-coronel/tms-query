import pymysql
import os
import re

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='db_tms',
)
cursor = conn.cursor()

# Output folder
output_folder = "generated_exports"
os.makedirs(output_folder, exist_ok=True)

# Read SQL file
file_path = "settings_queries\\settings.txt"
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Parse queries
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

# Function to extract alias from FROM clause
def extract_table_alias(query):
    match = re.search(r"FROM\s+[\w\.]+\s+AS\s+(\w+)", query, re.IGNORECASE)
    return match.group(1) if match else None

# Function to infer CREATE TABLE statement from SELECT query
def generate_create_table_sql(table_name, columns):
    col_defs = []
    for name, type_code in columns:
        if 'int' in str(type_code).lower():
            col_type = 'INT'
        elif 'decimal' in str(type_code).lower():
            col_type = 'DECIMAL(10,2)'
        elif 'date' in str(type_code).lower():
            col_type = 'DATE'
        elif 'datetime' in str(type_code).lower():
            col_type = 'DATETIME'
        else:
            col_type = 'VARCHAR(255)'
        col_defs.append(f"`{name}` {col_type}")
    
    cols_sql = ",\n    ".join(col_defs)
    return f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n    {cols_sql}\n);\n"

# Function to generate INSERT statements
def generate_insert_sql(table_name, columns, rows):
    insert_statements = []
    col_names = ', '.join([f"`{name}`" for name, _ in columns])
    for row in rows:
        values = []
        for val in row:
            if isinstance(val, str):
                values.append(f"'{val.replace('\'', '\'\'')}'")  # Escape single quotes
            elif val is None:
                values.append("NULL")
            else:
                values.append(str(val))
        value_str = ', '.join(values)
        insert_statements.append(f"INSERT INTO `{table_name}` ({col_names}) VALUES ({value_str});")
    return insert_statements

# Write all output to a single .sql file
sql_output_file = os.path.join(output_folder, "exported_data_structure_full.sql")
with open(sql_output_file, 'w', encoding='utf-8') as sqlfile:

    for idx, query in enumerate(queries):
        if query.lower().startswith("select"):
            table_alias = extract_table_alias(query)
            if not table_alias:
                table_alias = f"table_{idx+1}"

            cursor.execute(query)
            rows = cursor.fetchall()
            desc = cursor.description
            columns = [(desc[i][0], desc[i][1]) for i in range(len(desc))]

            # Create separate file per table
            sqlfile_path = os.path.join(output_folder, f"{table_alias}.sql")
            with open(sqlfile_path, 'w', encoding='utf-8') as sqlfile_out:
                sqlfile_out.write("-- Structure\n")
                sqlfile_out.write(generate_create_table_sql(table_alias, columns))
                sqlfile_out.write("\n-- Data\n")
                inserts = generate_insert_sql(table_alias, columns, rows)
                for stmt in inserts:
                    sqlfile_out.write(stmt + "\n")

            print(f"Exported: {sqlfile_path}")

print(f"✅ SQL export completed: {sql_output_file}")

cursor.close()
conn.close()