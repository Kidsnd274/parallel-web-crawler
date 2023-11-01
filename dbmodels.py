TABLES = {}

TABLES['serverinfo'] = (
    "CREATE TABLE serverinfo ("
    "  server_id SERIAL PRIMARY KEY,"
    "  ip_address VARCHAR(255) UNIQUE NOT NULL,"
    "  geolocation VARCHAR(255) NOT NULL"
    ");"
)

TABLES['pages'] = (
    "CREATE TABLE pages ("
    "  page_id SERIAL PRIMARY KEY,"
    "  url VARCHAR(2048) UNIQUE NOT NULL,"
    "  response_time DOUBLE PRECISION,"
    "  server_id INTEGER REFERENCES serverinfo(server_id),"
    "  visited BOOLEAN DEFAULT FALSE"
    ");"
)

TABLES['data'] = (
    "CREATE TABLE data ("
    "   page_id INTEGER PRIMARY KEY REFERENCES pages(page_id),"
    "   content TEXT"
    ");"
)