def inject_config(self):
    import os
    if 'ANSIBLE_CONFIG' not in os.environ:
        os.environ['ANSIBLE_CONFIG'] = self.ansible_config_path