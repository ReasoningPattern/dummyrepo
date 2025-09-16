import yaml

def _dump_string(obj, dumper=None):
    """
    Given a python object and serialize it into a YAML stream

    Args:
        obj: python object

    Returns:
        YAML stream
    """
    if dumper is None:
        dumper = yaml.Dumper
    return yaml.dump(obj, Dumper=dumper)