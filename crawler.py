import urllib.parse
import requests
from bs4 import BeautifulSoup

class CrawlInfo:
    def __init__(self, ip_addresss, response_time, geolocation, html, url_list):
        self.ip_address = ip_addresss
        self.response_time = response_time
        self.geolocation = geolocation
        self.html = html
        self.url_list = url_list
        
    def get_info(self):
        return (self.ip_address, self.response_time, self.geolocation)
    
class Crawler: # Takes in one URL and returns a list of URLs in that page
    def __init__(self, url):
        self.url = url
        self.url_list = []
        self.crawl_info = None
    
    def start_crawling(self):
        if self.crawl_info is None:
            raise Exception # This Crawler has already been ran
        
        # Download html
        r = requests.get(self.url)
        if r.status_code != 200:
            return []
            raise Exception # Raise exception that url failed to crawl
        
        html = r.text
        
        # Extract urls
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            href_url = link.get('href')
            if href_url and href_url.startswith('/'):
                href_url = urllib.parse.urljoin(self.url, href_url)
            self.url_list.append(href_url)
        
        return self.get_url_list()
    
    def get_url_list(self):
        return self.url_list


if __name__ == "__main__":
    try:
        import sys
        url = sys.argv[1]
    except IndexError:
        print("Please input an URL!")
    test_crawler = Crawler(url)
    print(test_crawler.start_crawling())
    