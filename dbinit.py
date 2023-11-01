import psycopg2
from dbutils import connect_to_db
from dbmodels import TABLES

def initialize_database():
    # Connect to the database
    conn = connect_to_db()
    cursor = conn.cursor()

    # Create the tables using the SQL statements from models.py
    for table_name, creation_sql in TABLES.items():
        cursor.execute(creation_sql)

    # Commit changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    initialize_database()
