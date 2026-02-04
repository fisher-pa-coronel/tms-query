import pymysql

# Connect to MySQL (XAMPP uses 'localhost', default user 'root', empty password usually)
connection = pymysql.connect(
    host="localhost",
    user="root",        # Default user for XAMPP MySQL
    password="",         # Default password is empty
    port=3306,        # Default MySQL port
)
print(connection)

# Create a cursor object
cursor = connection.cursor()

# Execute query to show all databases
cursor.execute("SHOW DATABASES")

# Fetch and print all databases
print("List of databases:")
for db in cursor:
    print(db[0])

# Close cursor and connection
cursor.close()
connection.close()