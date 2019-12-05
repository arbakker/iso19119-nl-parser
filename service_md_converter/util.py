from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

def get_service_cap_key(ogc_service_type):
    ogc_service_type_lower = ogc_service_type.lower()
    return f"service_capabilities_url_{ogc_service_type_lower}"

def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False