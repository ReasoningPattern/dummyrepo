def unit_of_work(metadata=None, timeout=None):
    def decorator(func):
        func.metadata = metadata
        func.timeout = timeout
        return func
    return decorator