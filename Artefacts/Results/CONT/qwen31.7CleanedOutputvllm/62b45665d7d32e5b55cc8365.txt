import argparse

def parse_arguments(*unparsed_arguments):
    parser = argparse.ArgumentParser()
    for arg in unparsed_arguments:
        parser.add_argument(arg)
    args = parser.parse_args()
    return vars(args)