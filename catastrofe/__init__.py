"""
Catastrofe - Eina per processar dades del Cadastre espanyol
"""

from .xml_splitter import XMLSplitter
from .csv_exporter import CatastroCSVExporter

try:
    from importlib.metadata import version
    __version__ = version("catastrofe")
except Exception:
    __version__ = "unknown"

__all__ = ["XMLSplitter", "CatastroCSVExporter"]
