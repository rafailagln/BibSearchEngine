# __init__.py

print("Initializing my_package...")

from .read_config import IniConfig, JsonConfig

__all__ = ['IniConfig', 'JsonConfig']