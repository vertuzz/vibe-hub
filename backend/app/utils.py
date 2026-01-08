import re
import random
import string
from urllib.parse import urlparse

def slugify(text: str) -> str:
    """
    Convert a string to a slug.
    1. Handle None/Empty
    2. Convert to lowercase
    3. Replace non-alphanumeric characters with hyphens
    4. Remove multiple hyphens
    5. Strip leading/trailing hyphens
    """
    if not text:
        return "app"
        
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text)
    res = text.strip('-')
    return res if res else "app"

def generate_unique_slug(base_slug: str) -> str:
    """
    Generate a unique slug by appending a random suffix.
    This is a helper; uniqueness checks should still be done against the DB.
    """
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_slug}-{suffix}"


def normalize_url(url: str | None) -> str | None:
    """
    Normalize a URL for consistent comparison.
    
    - Strips protocol (http://, https://)
    - Removes 'www.' prefix
    - Removes trailing slashes
    - Lowercases the result
    
    Returns None if input is None or empty.
    """
    if not url:
        return None
    
    url = url.strip().lower()
    
    # Parse the URL to handle it properly
    parsed = urlparse(url)
    
    # If no scheme, urlparse puts everything in path
    if parsed.netloc:
        host = parsed.netloc
        path = parsed.path
    else:
        # URL didn't have scheme, treat the whole thing as host+path
        # Try adding a scheme and re-parse
        parsed = urlparse(f"https://{url}")
        host = parsed.netloc
        path = parsed.path
    
    # Remove www. prefix
    if host.startswith('www.'):
        host = host[4:]
    
    # Remove trailing slashes from path
    path = path.rstrip('/')
    
    # Reconstruct normalized URL (host + path + query if present)
    result = host + path
    if parsed.query:
        result += '?' + parsed.query
    
    return result if result else None
