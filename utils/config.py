import os

def load_config(config_file_path=None):
    """Loads configuration from a .env style file or environment variables.

    Args:
        config_file_path (str, optional): Path to the configuration file.
            If None, defaults to 'config/config.env'.

    Returns:
        dict: A dictionary containing the configuration values.
    """

    if config_file_path is None:
        config_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config', 'config.env'
        )

    config = {}

    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key] = value.strip('"')
    else:
        print(f"Warning: Configuration file not found at {config_file_path}")

    # Override with environment variables if they exist
    for key, value in os.environ.items():
        config[key] = value

    return config