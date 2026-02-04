import os
import csv
import pymysql
import shutil
from datetime import datetime

# Configuration
CSV_FOLDER = 'generated_exports'
INSERTED_FOLDER = os.path.join(CSV_FOLDER, 'inserted')
LOG_FILE_PATH = os.path.join(INSERTED_FOLDER, 'import_log.txt')

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

def log_import(log_path, message):
    """Write timestamped log entry"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def import_csv_to_table(cursor, connection, csv_path):
    filename = os.path.basename(csv_path)
    table_name = os.path.splitext(filename)[0]
    print(f"\n🔄 Processing: {filename} → Table: `{table_name}`")

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)

            # Basic type detection from first row
            sample_row = next(reader, None)
            if not sample_row:
                print(f"⚠️ Skipping empty file: {csv_path}")
                return 0

            column_types = {h: get_sql_friendly_type(v) for h, v in zip(headers, sample_row)}

            # Re-read file
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

            cursor.executemany(insert_sql, values_to_insert)
            connection.commit()
            count = len(values_to_insert)
            print(f"✅ Inserted {count} rows into `{table_name}`")
            log_import(LOG_FILE_PATH, f"Imported '{filename}' → {count} rows into `{table_name}`")
            return count

    except Exception as e:
        print(f"❌ Error inserting into `{table_name}`: {e}")
        log_import(LOG_FILE_PATH, f"❌ ERROR importing '{filename}': {e}")
        return 0

# Main
if __name__ == '__main__':
    # Ensure inserted folder exists
    os.makedirs(INSERTED_FOLDER, exist_ok=True)

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Disable strict mode for this session only
    cursor.execute("SET SESSION sql_mode = ''")

    # Process all CSV files in main folder
    for filename in os.listdir(CSV_FOLDER):
        if filename.endswith('.csv') and not filename.startswith('inserted_'):
            file_path = os.path.join(CSV_FOLDER, filename)

            # Skip if already moved but not yet removed from list
            if file_path.startswith(INSERTED_FOLDER):
                continue

            # Import and move logic
            rows_inserted = import_csv_to_table(cursor, conn, file_path)
            if rows_inserted > 0:
                dest_path = os.path.join(INSERTED_FOLDER, filename)
                try:
                    shutil.move(file_path, dest_path)
                    print(f"📁 Moved '{filename}' → '{dest_path}'")
                    log_import(LOG_FILE_PATH, f"Moved '{filename}' to '{dest_path}'")
                except Exception as e:
                    print(f"⚠️ Failed to move '{filename}': {e}")
                    log_import(LOG_FILE_PATH, f"⚠️ Failed to move '{filename}': {e}")

    cursor.close()
    conn.close()
    print("\n✅ Import process completed.")