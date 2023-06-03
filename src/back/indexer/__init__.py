# __init__.py

print("Initializing my_package...")

from .data_reader import Reader
from .index_creator import IndexCreator
from .index_metadata import Metadata
from .index_valueInfo import InfoClass

__all__ = ['Reader', 'IndexCreator', 'Metadata', 'InfoClass']
