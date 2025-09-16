def _validate_labels(labels):
    """
    Check that keys and values in the given labels by validate_key() and validate_value().
    """
    for key, value in labels.items():
        if not validate_key(key):
            raise ValueError(f"Invalid key: {key}")
        if not validate_value(value):
            raise ValueError(f"Invalid value: {value}")