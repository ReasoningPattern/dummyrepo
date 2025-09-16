import re

def get_pattern(pattern, strip=True):
    if isinstance(pattern, str):
        if strip:
            pattern = pattern.strip()
        return re.compile(pattern)
    else:
        return pattern