# simulation/utils.py

def validate_config(user_config, default_config):
    """
    Merge user-supplied config with default values.
    Any missing keys in user_config are filled with values from default_config.
    """
    config = default_config.copy()
    config.update(user_config)
    return config