from urllib.parse import urljoin, urlparse

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

if __name__ == "__main__": # Test code to test the crawler for one URL
    try:
        import sys
        url = sys.argv[1]
    except IndexError:
        print("Please input an URL!")
    print(is_valid_link(url))
    # print(ensure_absolute_url("https://en.wikipedia.org", url))
    print(ensure_schema_added(url))