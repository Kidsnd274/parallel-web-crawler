from database import Database

# Sample data for testing
URLS = [
    ("http://example1.com", 0.5),
    ("http://example2.com", 0.6),
]

SERVER_INFO = [
    ("192.168.1.1", "US"),
    ("192.168.1.2", "UK"),
]

PAGE_DATA = [
    ("http://example1.com", "Some content for example1.com"),
    ("http://example2.com", "Some content for example2.com"),
]

# Instantiate Database connection
db = Database('crawler.db')
db.clear_all()

# Insert server info
for ip, location in SERVER_INFO:
    db.get_or_insert_server_info(ip, location)

# Insert URLs and associate them with a server
server_id = 1
for url, response_time in URLS:
    print(url)
    db.insert_url(url, response_time, server_id)
    server_id += 1

# Insert page content data
page_id = 1
for url, content in PAGE_DATA:

    db.insert_data(page_id, content)
    page_id += 1

# check if url visited
print("check url visited")
print(db.check_url_visited("http://example2.com"))

# Fetch and print data
print("\nAll URLs:")
print(db.fetch_all_urls())

print("\nAll Server Info:")
print(db.fetch_all_server_info())

print("\nAll Page Data:")
print(db.fetch_all_data())

# You can also test the fetch_data_by_page_id method by specifying a valid page_id.
print("\nData for Page ID 1:")
print(db.fetch_data_by_page_id(1))
