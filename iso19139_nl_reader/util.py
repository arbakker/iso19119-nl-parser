from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False