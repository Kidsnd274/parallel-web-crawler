import sqlite3

class Database():
    def __init__(self, db_name, db_lock):
        self.db_name = db_name
        self.lock = db_lock # Database lock shared with other processes
        self.conn = None
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_database(self): # Initialize and create new database with specified tables
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

        # cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS data (
        #         page_id INTEGER PRIMARY KEY,
        #         content TEXT,
        #         FOREIGN KEY (page_id) REFERENCES pages(page_id)
        #     );
        # """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS genre_mentions (
                keyword TEXT UNIQUE NOT NULL,
                count INTEGER DEFAULT 0,
                CHECK (count >= 0)
            );
        """)

        self.conn.commit()

    # Function to add crawl results from a CrawlInfo object into the database
    def add_server_info_and_url(self, crawl_info): # Only use this function for the Crawler class
        url_crawled = crawl_info.url_crawled
        ip_address = crawl_info.ip_address
        response_time = crawl_info.response_time
        country = crawl_info.country
        city = crawl_info.city
        # html_data = crawl_info.html
        key_dict = crawl_info.key_dict
        
        # print(f"[INFO] Database attempting lock with {url_crawled}")
        with self.lock:
            # print(f"[INFO] Database GOT lock with {url_crawled}")

            self.connect()

            if not self.check_url_visited_without_lock(url_crawled): # Check if URL is in database
                db_server_id = self.get_or_insert_server_info(ip_address, country, city) # Add server info
                self.insert_url(url_crawled, response_time, db_server_id) # Add page info
                self.update_keywords(key_dict)
            else:
                print(f"[WARNING] Database encountered duplicate URL {url_crawled}")

            self.close()
            
        # print(f"[INFO] Database RELEASED lock with {url_crawled}")

    def check_url_visited(self, url): # Only use this function for the Crawler class
        # print(f"[INFO] Database check attempting lock with {url}")
        with self.lock:
            # print(f"[INFO] Database check GOT lock with {url}")
            self.connect()
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("SELECT visited FROM pages WHERE url = ?;", (url,))
                result = cur.fetchone()
            self.close()
        # print(f"[INFO] Database check RELEASED lock with {url}")
        if result is None:
            return False
        else:
            return True
        
    def check_url_visited_without_lock(self, url):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT visited FROM pages WHERE url = ?;", (url,))
            result = cur.fetchone()
        if result is None:
            return False
        else:
            return True

    def get_or_insert_server_info(self, ip_address, country, city):
        try:
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
        except sqlite3.IntegrityError as e:
            print(f"[ERROR] Error inserting server info '{ip_address}: {e}")
            return 0

    def insert_url(self, url, response_time, server_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO pages (url, response_time, server_id) VALUES (?, ?, ?)",
                            (url, response_time, server_id))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"[ERROR] Error inserting URL '{url}: {e}")

        return cursor.lastrowid        

    def mark_page_as_visited(self, page_id):
        cursor = self.conn.cursor()

        cursor.execute("UPDATE pages SET visited = TRUE WHERE page_id = ?", (page_id,))
        self.conn.commit()

    # def insert_data(self, page_id, data):
    #     cursor = self.conn.cursor()

    #     cursor.execute("INSERT INTO data (page_id, content) VALUES (?, ?)", (page_id, data))
    #     self.conn.commit()

    def update_keywords(self, keyword_dict):
        cursor = self.conn.cursor()
        for keyword, count in keyword_dict.items():
            try:
                if count < 0: # Ensure that count more than 0
                    print(f"[ERROR] Database received negative count for keyword '{keyword}'")
                    continue
                
                # Check if keyword already exists
                cursor.execute("SELECT count FROM genre_mentions WHERE keyword = ?", (keyword,))
                result = cursor.fetchone()
                
                if result: # If keyword exists, increment the count
                    new_count = result[0] + count
                    if new_count >= 0: # Check if new count is valid
                        cursor.execute("UPDATE genre_mentions SET count = ? WHERE keyword = ?", (new_count, keyword))
                    else:
                        print(f"[ERROR] Database attempted to update count < 0 for keyword '{keyword}' and new count {new_count}")
                        continue
                else: # Create new keyword
                    cursor.execute("INSERT INTO genre_mentions (keyword, count) VALUES (?, ?)", (keyword, count))
            except sqlite3.IntegrityError as e:
                print(f"[ERROR] Error updating keyword '{keyword}: {e}")
        
        self.conn.commit() # Move this into the for loop if you want to save after every keyword

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
            
    def fetch_all_keyword_count(self):
        """Retrieve all content data from the data table."""
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT keyword, count FROM genre_mentions;")
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
