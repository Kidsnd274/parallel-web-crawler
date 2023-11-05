from ipaddress import ip_address
from urllib.parse import urljoin, urlparse
import requests
import socket
from bs4 import BeautifulSoup

class CrawlInfo:
    def __init__(self, ip_address, response_time, geolocation, html, url_list):
        self.ip_address = ip_address
        self.response_time = response_time
        self.country = geolocation["country"]
        self.city = geolocation["city"]
        self.html = html
        self.url_list = url_list
        
    def __str__(self):
        return str(self.url_list)
    
    def get_info(self):
        return (self.ip_address, self.response_time, self.country, self.city)
    
class Crawler: # Takes in one URL and returns a list of URLs in that page
    database_ref = None
    
    def __init__(self, url):
        self.url = Crawler.ensure_schema_added(url)
        self.crawl_info = None
        
    @staticmethod
    def set_database(ref): # Call this during initialization
        Crawler.database_ref = ref
    
    def is_valid_link(link):
        parsed_href = urlparse(link)
        
        # Check if it's not a http or https link
        if parsed_href.scheme in ['mailto', 'tel', 'javascript']:
            return False
        
        # Check if it's an anchor link
        if link.startswith('#'):
            return False
            
        return True

    def ensure_absolute_url(base_url, link): # Checks if it's a relative path and adds the base_url
        if bool(urlparse(link).netloc):
            return link
        return urljoin(base_url, link)

    def ensure_schema_added(link):
        parsed_href = urlparse(link)
        
        if parsed_href.scheme == '': # Checks if link does not have a scheme and adds https by default
            new_parsed_href = urlparse(f"https://{parsed_href.geturl()}")
            return new_parsed_href.geturl()
        return parsed_href.geturl()
        
    
    def start_crawling(self):
        if self.crawl_info is not None: # Raise an exception if this URL has already been crawled
            raise Exception(f'URL {self.url} has already been crawled')
        
        # Check with db if this url has been crawled
        
        
        # Download HTML from URL
        r = requests.get(self.url)
        if r.status_code != 200:
            return None
        
        html = r.text
        
        # Extract URLs from HTML content
        url_list = []
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            href_url = link.get('href')
            if Crawler.is_valid_link(href_url):
                href_url = Crawler.ensure_absolute_url(self.url, href_url)
                url_list.append(href_url)
        
        # Extract IP address, response time and geolocation
        ip_address = Crawler.get_ip_address(self.url)
        response_time = r.elapsed.total_seconds()
        geolocation = Crawler.get_location(ip_address)
        
        results = CrawlInfo(ip_address=ip_address, response_time=response_time, geolocation=geolocation, html=html, url_list=url_list)
        self.crawl_info = results
        
        # Add to database
        
        return results
    
    def get_ip_address(url):
        domain = url.split("://")[-1].split("/")[0]
        return socket.gethostbyname(domain)
    
    def get_location(ip_address):
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        data = response.json()
        return data
    
    def get_url_list(self):
        return self.crawl_info.url_list


if __name__ == "__main__": # Test code to test the crawler for one URL
    try:
        import sys
        url = sys.argv[1]
    except IndexError:
        print("Please input an URL!")
    test_crawler = Crawler(url)
    test_crawler.start_crawling()

    results = test_crawler.crawl_info
    if (results is None):
        print("URL invalid")
    else:
        print(f"IP Address: {str(results.ip_address)}")
        print(f"Response Time: {str(results.response_time)}s")
        print(f"Geolocation:")
        print(f"\tCountry: {str(results.country)}")
        print(f"\tCity: {str(results.city)}")
        print(f"URLS: {str(results.url_list)}")
    