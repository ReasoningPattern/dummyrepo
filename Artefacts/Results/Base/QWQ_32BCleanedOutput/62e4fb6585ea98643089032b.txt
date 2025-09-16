def parse_version(s: str) -> tuple[int, ...]:
    return tuple(int(part) for part in s.split('.'))