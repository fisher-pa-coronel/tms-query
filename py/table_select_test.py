import pymysql
from prettytable import PrettyTable

# === Pre-defined database connection variables ===
HOST = "localhost"
USER = "root"
PASSWORD = ""
DATABASE = "db_tms"
PORT = 3306
TABLE_NAME = "tinfile"
# =================================================

def print_table():
    # Connect to MySQL database
    conn = pymysql.connect(
        host = HOST,
        user = USER,
        password = PASSWORD,
        port= PORT,
        database = DATABASE
    )
    cursor = conn.cursor()

    try:
        # Fetch all rows from the table
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Use PrettyTable to format output
        table = PrettyTable()
        table.field_names = columns
        for row in rows:
            table.add_row(row)
        
        print(f"Contents of table `{TABLE_NAME}`:")
        print(table)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print_table()