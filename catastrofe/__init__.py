"""
Catastrofe - Eina per processar dades del Cadastre espanyol
"""

from .xml_splitter import XMLSplitter
from .csv_exporter import CatastroCSVExporter

__version__ = "1.0.0"
__all__ = ["XMLSplitter", "CatastroCSVExporter"]
