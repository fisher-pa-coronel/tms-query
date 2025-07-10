import os
import csv
import pymysql
import re

# Configuration
CSV_FOLDER = 'generated_exports'
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'tms_test_migration',  # ← Change to your target database
    'charset': 'utf8mb4'
}

def get_sql_friendly_type(value):
    """Basic type inference for CREATE TABLE"""
    if value is None:
        return "TEXT"
    try:
        int(value)
        return "INT"
    except (ValueError, TypeError):
        try:
            float(value)
            return "DECIMAL(18,2)"
        except (ValueError, TypeError):
            return "TEXT"

def create_table_if_not_exists(cursor, table_name, columns_and_types):
    cols = []
    for col, dtype in columns_and_types.items():
        cols.append(f"`{col}` {dtype}")
    col_defs = ",\n  ".join(cols)
    create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n  {col_defs}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
    cursor.execute(create_sql)

def import_csv_to_table(cursor, connection, table_name, csv_path):
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

        # Basic type detection from first row of data
        sample_row = next(reader, None)
        if not sample_row:
            print(f"⚠️ Skipping empty file: {csv_path}")
            return

        column_types = {}
        for col, val in zip(headers, sample_row):
            column_types[col] = get_sql_friendly_type(val)

        # Re-read file from beginning
        f.seek(0)
        reader = csv.DictReader(f)

        # Prepare insert statement
        columns = ', '.join([f"`{h}`" for h in headers])
        placeholders = ', '.join(['%s'] * len(headers))
        insert_sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

        values_to_insert = []
        for row in reader:
            values = [row[h] for h in headers]
            values_to_insert.append(tuple(values))

        try:
            cursor.executemany(insert_sql, values_to_insert)
            connection.commit()
            print(f"✅ Inserted {len(values_to_insert)} rows into `{table_name}`")
        except Exception as e:
            print(f"❌ Error inserting into `{table_name}`: {e}")

# Main
if __name__ == '__main__':
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for filename in os.listdir(CSV_FOLDER):
        if filename.endswith('.csv'):
            table_name = os.path.splitext(filename)[0]
            file_path = os.path.join(CSV_FOLDER, filename)

            print(f"\n🔄 Processing: {filename} → Table: `{table_name}`")

            try:
                # Optional: Create table based on CSV header + basic type guess
                with open(file_path, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    sample_row = next(reader, None)
                    if sample_row:
                        column_types = {h: get_sql_friendly_type(v) for h, v in zip(headers, sample_row)}
                        # create_table_if_not_exists(cursor, table_name, column_types)

                # Import data
                import_csv_to_table(cursor, conn, table_name, file_path)

            except Exception as e:
                print(f"⚠️ Failed to process {filename}: {e}")

    cursor.close()
    conn.close()