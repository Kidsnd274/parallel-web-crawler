from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def canonicalize_url(url):
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
    print(type(parsed_url.query))
    print(parsed_url.query)
    query = urlencode(sorted(parse_qsl(parsed_url.query)))
    
    # Reconstruct the URL from components
    canonicalized_url = urlunparse((scheme, netloc, path, parsed_url.params, query, ''))
    
    return canonicalized_url

# Example usage
url = "HTTP://www.Example.com:80//A/B/../C/./D.html?b=2&a=1&b=3"
print(canonicalize_url(url))
