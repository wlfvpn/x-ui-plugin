import yaml


def load_config(path='config.yaml'):
    with open(path, 'r') as stream:
        config = yaml.safe_load(stream)
    return config
    