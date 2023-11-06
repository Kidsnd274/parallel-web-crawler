import sqlite3
import multiprocessing as mp

# Example usage:
# db = Database("your_database_name.db")
# db.initialize()

class Database():
    def __init__(self, db_name, db_lock):
        self.db_name = db_name
        # self.lock = threading.Lock()
        self.lock = db_lock
        self.conn = None
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_database(self):   
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS serverinfo (
                server_id INTEGER PRIMARY KEY,
                ip_address TEXT UNIQUE NOT NULL,
                country TEXT NOT NULL,
                city TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                page_id INTEGER PRIMARY KEY,
                url TEXT UNIQUE NOT NULL,
                response_time REAL,
                server_id INTEGER,
                visited BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (server_id) REFERENCES serverinfo(server_id)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                page_id INTEGER PRIMARY KEY,
                content TEXT,
                FOREIGN KEY (page_id) REFERENCES pages(page_id)
            );
        """)

        self.conn.commit()

    def check_url_visited(self, url):
        with self.lock:
            self.connect()
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("SELECT visited FROM pages WHERE url = ?;", (url,))
                result = cur.fetchone()
            self.close()
        return result[0] if result else None

    def get_or_insert_server_info(self, ip_address, country, city):
        cursor = self.conn.cursor()

        cursor.execute("SELECT server_id FROM serverinfo WHERE ip_address = ?", (ip_address,))
        server_id = cursor.fetchone()

        if server_id is None:
            cursor.execute("INSERT INTO serverinfo (ip_address, country, city) VALUES (?, ?, ?)",
                            (ip_address, country, city))
            self.conn.commit()
            server_id = cursor.lastrowid
        else:
            server_id = server_id[0]
        return server_id

    def insert_url(self, url, response_time, server_id):
        cursor = self.conn.cursor()

        cursor.execute("INSERT INTO pages (url, response_time, server_id) VALUES (?, ?, ?)",
                        (url, response_time, server_id))
        self.conn.commit()
        return cursor.lastrowid
        
    def add_server_info_and_url(self, crawl_info): # For Crawler's use
        url_crawled = crawl_info.url_crawled
        ip_address = crawl_info.ip_address
        response_time = crawl_info.response_time
        country = crawl_info.country
        city = crawl_info.city
        html_data = crawl_info.html
        
        # try: # Add logging
        # print(f"Attempting to get lock... {url_crawled}")
        with self.lock:
            # print(f"Got Lock {url_crawled}")
            self.connect()
            db_server_id = self.get_or_insert_server_info(ip_address, country, city) # Add server info
            db_page_id = self.insert_url(url_crawled, response_time, db_server_id)
            # self.insert_data(db_page_id, html_data) # causes program to hang
            self.close()
        

    def mark_page_as_visited(self, page_id):
        with self.lock:
            cursor = self.conn.cursor()

            cursor.execute("UPDATE pages SET visited = TRUE WHERE page_id = ?", (page_id,))
            self.conn.commit()

    def insert_data(self, page_id, data):
        with self.lock:
            cursor = self.conn.cursor()

            cursor.execute("INSERT INTO data (page_id, content) VALUES (?, ?)", (page_id, data))
            self.conn.commit()


    def fetch_all_urls(self):
        """Retrieve all URLs from the pages table."""
        with self.lock:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("SELECT page_id, url, response_time, server_id, visited FROM pages;")
                return cur.fetchall()

    def fetch_all_server_info(self):
        """Retrieve all server information from the serverinfo table."""
        with self.lock:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("SELECT server_id, ip_address, geolocation FROM serverinfo;")
                return cur.fetchall()

    def fetch_data_by_page_id(self, page_id):
        """Retrieve content data for a specific page_id from the data table."""
        with self.lock:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("SELECT content FROM data WHERE page_id = ?;", (page_id,))
                result = cur.fetchone()
                return result[0] if result else None

    def fetch_all_data(self):
        """Retrieve all content data from the data table."""
        with self.lock:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("SELECT page_id, content FROM data;")
                return cur.fetchall()

    ### PLEASE USE THIS WITH CAUTION, CLEARS EVERYTHING IN DATABASE!!!
    def clear_all(self):
        with self.lock:
            cursor = self.conn.cursor()

            try:
                # Clear data from the 'data' table
                cursor.execute("DELETE FROM data;")

                # Clear data from the 'pages' table
                cursor.execute("DELETE FROM pages;")

                # Clear data from the 'serverinfo' table
                cursor.execute("DELETE FROM serverinfo;")

                # Commit the changes
                self.conn.commit()
            finally:
                cursor.close()





