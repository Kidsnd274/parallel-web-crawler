from ipaddress import ip_address
import urllib.parse
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
    def __init__(self, url):
        self.url = url
        self.crawl_info = None
    
    def start_crawling(self):
        if self.crawl_info is not None:
            raise Exception # This Crawler has already been ran
        
        # Download html
        r = requests.get(self.url)
        if r.status_code != 200:
            return []
            raise Exception # Raise exception that url failed to crawl
        
        html = r.text
        
        # Extract urls
        url_list = []
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            href_url = link.get('href')
            if href_url and href_url.startswith('/'):
                href_url = urllib.parse.urljoin(self.url, href_url)
            url_list.append(href_url)
        
        # Extract IP address, response time and geolocation
        ip_address = Crawler.get_ip_address(url)
        response_time = r.elapsed.total_seconds()
        geolocation = Crawler.get_location(ip_address)

        results = CrawlInfo(ip_address=ip_address, response_time=response_time, geolocation=geolocation, html=html, url_list=url_list)
        self.crawl_info = results
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


if __name__ == "__main__":
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
    