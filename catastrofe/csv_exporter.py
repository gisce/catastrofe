#!/usr/bin/env python3
"""
CSV Exporter - Exporta dades del Cadastre a CSV
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
import zipfile
import csv
import tempfile
import shutil

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()


class CatastroCSVExporter:
    """Classe per exportar dades del Cadastre a CSV."""
    
    FIELDS = [
        'TV', 'NV', 'PNP', 'PLP', 'BQ', 'ES', 'PT', 'PU',
        'PCA_CAR_CDC1_CDC2',  # Concatenat
        'PCA', 'CAR', 'CDC1', 'CDC2',
        'CPO', 'CPA', 'KM', 'ESC', 'PLA', 'PUE', 'POL', 'PAR',
        'SNP', 'SLP', 'KK'
    ]
    
    def __init__(self, input_files: List[Path], output_file: Path, verbose: bool = True):
        self.input_files = input_files
        self.output_file = output_file
        self.verbose = verbose
        self.temp_dir = None
    
    def extract_zip(self, zip_path: Path) -> List[Path]:
        """Extreu fitxers XML d'un zip."""
        xml_files = []
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for name in zip_ref.namelist():
                if name.lower().endswith('.xml'):
                    extract_path = self.temp_dir / name
                    zip_ref.extract(name, self.temp_dir)
                    xml_files.append(extract_path)
        return xml_files
    
    def get_text(self, element: Optional[ET.Element], tag: str) -> str:
        """Obté el text d'un subelement, retorna string buit si no existeix."""
        if element is None:
            return ''
        child = element.find(tag)
        return child.text.strip() if child is not None and child.text else ''
    
    def extract_bie_data(self, bie: ET.Element) -> Dict[str, str]:
        """Extreu les dades d'un element BIE."""
        data = {}
        
        # RCA dins IBI - Referència cadastral
        ibi = bie.find('IBI')
        rca = ibi.find('RCA') if ibi is not None else None
        data['PCA'] = self.get_text(rca, 'PCA')
        data['CAR'] = self.get_text(rca, 'CAR')
        data['CDC1'] = self.get_text(rca, 'CDC1')
        data['CDC2'] = self.get_text(rca, 'CDC2')
        
        # Concatenat
        data['PCA_CAR_CDC1_CDC2'] = f"{data['PCA']}{data['CAR']}{data['CDC1']}{data['CDC2']}"
        
        # DIR - Adreça (només propietats urbanes)
        dir_section = bie.find('.//DIR')
        data['TV'] = self.get_text(dir_section, 'TV')
        data['NV'] = self.get_text(dir_section, 'NV')
        data['PNP'] = self.get_text(dir_section, 'PNP')
        data['PLP'] = self.get_text(dir_section, 'PLP')
        data['BQ'] = self.get_text(dir_section, 'BQ')
        data['KM'] = self.get_text(dir_section, 'KM')
        
        # LOINT - Localització dins edifici (només propietats urbanes)
        loint = bie.find('.//LOINT')
        data['ES'] = self.get_text(loint, 'ES')
        data['PT'] = self.get_text(loint, 'PT')
        data['PU'] = self.get_text(loint, 'PU')
        
        # CPP - Polígon i parcel·la
        cpp = bie.find('.//CPP')
        data['CPO'] = self.get_text(cpp, 'CPO')
        data['CPA'] = self.get_text(cpp, 'CPA')
        
        # LEC/ELC - Elements constructius (primer element)
        lec = bie.find('.//LEC')
        elc = lec.find('.//ELC') if lec is not None else None
        data['ESC'] = self.get_text(elc, 'ESC')
        data['PLA'] = self.get_text(elc, 'PLA')
        data['PUE'] = self.get_text(elc, 'PUE')
        
        # DT - Altres camps
        dt = bie.find('DT')
        data['POL'] = self.get_text(dt, 'POL')
        data['PAR'] = self.get_text(dt, 'PAR')
        
        # LCONS - Construccions
        lcons = dt.find('.//LCONS') if dt is not None else None
        data['SNP'] = self.get_text(lcons, 'SNP')
        data['SLP'] = self.get_text(lcons, 'SLP')
        
        # Altres
        data['KK'] = self.get_text(bie, 'KK')
        
        return data
    
    def process_xml(self, xml_path: Path) -> List[Dict[str, str]]:
        """Processa un fitxer XML i extreu totes les BIE."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        results = []
        for bie in root.findall('.//BIE'):
            data = self.extract_bie_data(bie)
            results.append(data)
        
        return results
    
    def export(self) -> int:
        """Exporta les dades a CSV."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Recull tots els fitxers XML
            xml_files = []
            for input_file in self.input_files:
                if input_file.suffix.lower() == '.zip':
                    if self.verbose:
                        console.print(f"[cyan]📦 Extraient:[/cyan] {input_file.name}")
                    xml_files.extend(self.extract_zip(input_file))
                elif input_file.suffix.lower() == '.xml':
                    xml_files.append(input_file)
            
            if not xml_files:
                console.print("[red]✗ No s'han trobat fitxers XML[/red]")
                return 1
            
            # Processa tots els XMLs
            all_data = []
            
            if self.verbose:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=console
                ) as progress:
                    task = progress.add_task("[cyan]Processant XMLs...", total=len(xml_files))
                    
                    for xml_file in xml_files:
                        data = self.process_xml(xml_file)
                        all_data.extend(data)
                        progress.update(task, advance=1)
            else:
                for xml_file in xml_files:
                    data = self.process_xml(xml_file)
                    all_data.extend(data)
            
            # Escriu CSV
            if self.verbose:
                console.print(f"[cyan]💾 Guardant CSV:[/cyan] {self.output_file}")
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDS, delimiter=';')
                writer.writeheader()
                writer.writerows(all_data)
            
            if self.verbose:
                console.print(f"[green]✓ Exportades {len(all_data)} files[/green]")
            
            return 0
            
        finally:
            # Neteja temporal
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
