from ipaddress import ip_address
from urllib.parse import urlencode, urljoin, urlparse, parse_qs, parse_qsl, urlunparse
import random
import requests
import socket
from bs4 import BeautifulSoup
from htmlParser import htmlParser

class CrawlInfo:
    def __init__(self, url_crawled, ip_address, response_time, geolocation, url_list, key_dict):
        self.url_crawled = url_crawled
        self.ip_address = ip_address
        self.response_time = response_time
        self.country = geolocation.get("country", "Unknown")
        self.city = geolocation.get("city", "Unknown")
        self.geolocation = geolocation
        self.url_list = url_list
        self.key_dict = key_dict
        
    def __str__(self):
        return str(self.url_list)
    
    def get_info(self):
        return (self.ip_address, self.response_time, self.country, self.city)
    
class Crawler: # Takes in one URL and returns a list of URLs in that page
    def __init__(self, url):
        self.url = Crawler.ensure_schema_added(url)
        self.crawl_info = None
        self.db_ref = None
        
    def set_database(self, ref): # Sets the shared database's name
        self.db_ref = ref
    
    def is_valid_link(link): # Check URL link if it is a valid web link
        if link is None:
            return False
        
        parsed_url = urlparse(link)
        
        # Check if it's not a http or https link
        if parsed_url.scheme in ['mailto', 'tel', 'javascript']: # TODO: Might change this to check for http or https
            return False
        
        # Extract domain, sub-domain and query details
        if not parsed_url.hostname:
            domain = ''
        else:
            hostname_split = parsed_url.hostname.split('.')
            domain = '.'.join(hostname_split[-2:])
        subdomain = parsed_url.netloc.split('.')[0]
        query_params = parse_qs(parsed_url.query)
        
        # Ignore Steam website language links
        if (domain == 'steampowered.com' or domain == 'steamcommunity.com') and 'l' in query_params:
            return False
        
        # Ignore Wikipedia languages links
        wikipedia_lang_set = {'ar', 'bh', 'uk', 'hy', 'tl', 'fr', 'cv', 'inh', 'hr', 'sr', 'de', 'sl', 'pl', 'shn', 'no', 'ml', 'ru', 'pt', 'bn', 'fa', 'te', 'su', 'sq', 'ro', 'sv', 'ceb', 'ps', 'ku', 'nn', 'ne', 'ts', 'lv', 'tr', 'hi', 'sk', 'bg', 'as', 'km', 'mk', 'fy', 'fi', 'ckb', 'zh', 'el', 'et', 'ta', 'it', 'sd', 'sat', 'uz', 'bs', 'yi', 'vi', 'simple', 'azb', 'da', 'ja', 'my', 'hu', 'zh-min-nan', 'kk', 'ka', 'ga', 'si', 'eu', 'ca', 'tt', 'sh', 'ms', 'lt', 'zh-yue', 'cs', 'eo', 'gl', 'th', 'es', 'ast', 'pa', 'nl', 'he', 'ko', 'id'}
        if domain == 'wikipedia.org' and subdomain in wikipedia_lang_set:
            return False
        
        # Check if it's an anchor link
        if link.startswith('#'):
            return False
            
        return True

    def ensure_absolute_url(base_url, link): # Checks if it's a relative path and adds the base_url
        if bool(urlparse(link).netloc):
            return link
        return urljoin(base_url, link)

    def canonicalize_url(url): # Standardizes URLs for better duplicate URL handling  
        # Parse the URL into components
        parsed_url = urlparse(url)
        
        # Convert scheme and netloc to lowercase
        scheme = parsed_url.scheme.lower()
        netloc = parsed_url.netloc.lower()
        
        # Remove default port numbers (80 for http and 443 for https)
        if (scheme == "http" and netloc.endswith(':80')) or (scheme == "https" and netloc.endswith(':443')):
            netloc = netloc.rsplit(':', 1)[0]
        
        # Remove duplicate slashes
        path = parsed_url.path.replace('//', '/')
        
        # Sort query parameters
        query = urlencode(sorted(parse_qsl(parsed_url.query)))
        
        # Reconstruct the URL from components
        canonicalized_url = urlunparse((scheme, netloc, path, parsed_url.params, query, ''))
        
        return canonicalized_url


    def ensure_schema_added(link):  # Checks if link does not have a scheme and adds https by default
        parsed_href = urlparse(link)

        if parsed_href.scheme == '':
            new_parsed_href = urlparse(f"https://{parsed_href.geturl()}")
            return new_parsed_href.geturl()
        return parsed_href.geturl()
        
    
    def start_crawling(self): # Main crawling function
        db = self.db_ref
        
        if self.crawl_info is not None: # Raise an exception if this Crawler object has already been crawled
            raise Exception(f'URL {self.url} has already been crawled')
        
        # Check with db if this url has been crawled
        if db.check_url_visited(self.url):
            print(f"[INFO] Crawler found duplicate, skipping {self.url}")
            return None
        
        # Download HTML from URL
        try:
            r = requests.get(self.url, timeout=3)
        except requests.Timeout:
            print(f"[ERROR] Crawler request timed out for {self.url}")
            return None
        if r.status_code != 200:
            print(f"[ERROR] Received HTTP Code {r.status_code} from {self.url}")
            return None
        
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Compile information for html element
        key_dict = htmlParser.parse(html)
        
        # Extract URLs from HTML content
        url_list = []
        for link in soup.find_all('a'):
            href_url = link.get('href')
            href_url = Crawler.ensure_absolute_url(self.url, href_url)
            
            if Crawler.is_valid_link(href_url):
                href_url = Crawler.canonicalize_url(href_url)
                url_list.append(href_url)
        
        # Extract IP address, response time and geolocation
        ip_address = Crawler.get_ip_address(self.url)
        response_time = r.elapsed.total_seconds()
        geolocation = Crawler.get_location(ip_address)
        
        # Compile results into a CrawlInfo object
        results = CrawlInfo(url_crawled=self.url, ip_address=ip_address, 
                            response_time=response_time, geolocation=geolocation, 
                            url_list=url_list, key_dict= key_dict) # TODO: Consider only storing the <body> content of the HTML data OR process the data and store relevant data
        self.crawl_info = results
        
        if results == None:
            print(f"[WARNING] Crawler could not get HTML data even though 200 OK for {self.url}")
            return results

        db.add_server_info_and_url(results) # Add crawled data into database
        
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
    