import psycopg2

# Configuration variables
DB_NAME = "YOUR_DB_NAME"
DB_USER = "YOUR_DB_USER"
DB_PASSWORD = "YOUR_DB_PASSWORD"
DB_HOST = "localhost"
DB_PORT = "5432"


def connect_to_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def get_or_insert_server_info(cursor, ip_address, geolocation):
    cursor.execute("SELECT server_id FROM serverinfo WHERE ip_address = %s", (ip_address,))
    server_id = cursor.fetchone()

    if server_id is None:
        cursor.execute("INSERT INTO serverinfo (ip_address, geolocation) VALUES (%s, %s) RETURNING server_id;",
                       (ip_address, geolocation))
        server_id = cursor.fetchone()[0]
    else:
        server_id = server_id[0]

    return server_id


def insert_url(cursor, url, response_time, server_id):
    cursor.execute("INSERT INTO pages (url, response_time, server_id) VALUES (%s, %s, %s) RETURNING page_id;",
                   (url, response_time, server_id))
    return cursor.fetchone()[0]


def mark_page_as_visited(cursor, page_id):
    cursor.execute("UPDATE pages SET visited = TRUE WHERE page_id = %s;", (page_id,))


def insert_data(cursor, page_id, data):
    cursor.execute("INSERT INTO data (page_id, data) VALUES (%s, %s);",
                   (page_id, data))

