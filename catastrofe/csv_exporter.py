#!/usr/bin/env python3
"""
CSV Exporter - Exporta dades del Cadastre a CSV
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict
import zipfile
import csv
import tempfile
import shutil

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

console = Console()


def extract_text(element, tag):
    """
    Safely extract text from an XML element.
    Returns empty string if element or tag not found.
    """
    if element is None:
        return ''
    found = element.find('.//' + tag)
    return found.text.strip() if found is not None and found.text else ''


def process_bie_element(bie):
    """
    Extract all required fields from a BIE (property) element.
    Returns a dictionary with all fields.
    """
    rca = bie.find('.//RCA')
    pca = extract_text(rca, 'PCA')
    car = extract_text(rca, 'CAR')
    cdc1 = extract_text(rca, 'CDC1')
    cdc2 = extract_text(rca, 'CDC2')
    rc = f"{pca}{car}{cdc1}{cdc2}"
    
    dir_section = bie.find('.//DIR')
    tv = extract_text(dir_section, 'TV')
    nv = extract_text(dir_section, 'NV')
    pnp = extract_text(dir_section, 'PNP')
    plp = extract_text(dir_section, 'PLP')
    bq = extract_text(dir_section, 'BQ')
    km = extract_text(dir_section, 'KM')
    
    loint = bie.find('.//LOINT')
    es = extract_text(loint, 'ES')
    pt = extract_text(loint, 'PT')
    pu = extract_text(loint, 'PU')
    
    cpp = bie.find('.//CPP')
    cpo = extract_text(cpp, 'CPO')
    cpa = extract_text(cpp, 'CPA')
    
    lec = bie.find('.//LEC')
    elc = lec.find('.//ELC') if lec is not None else None
    esc = extract_text(elc, 'ESC')
    pla = extract_text(elc, 'PLA')
    pue = extract_text(elc, 'PUE')
    
    return {
        'TV': tv,
        'NV': nv,
        'PNP': pnp,
        'PLP': plp,
        'BQ': bq,
        'ES': es,
        'PT': pt,
        'PU': pu,
        'RC': rc,
        'PCA': pca,
        'CAR': car,
        'CDC1': cdc1,
        'CDC2': cdc2,
        'CPO': cpo,
        'CPA': cpa,
        'KM': km,
        'ESC': esc,
        'PLA': pla,
        'PUE': pue
    }


class CatastroCSVExporter:
    """Classe per exportar dades del Cadastre a CSV."""
    
    FIELDS = ['TV', 'NV', 'PNP', 'PLP', 'BQ', 'ES', 'PT', 'PU', 'RC', 
               'PCA', 'CAR', 'CDC1', 'CDC2', 'CPO', 'CPA', 'KM', 'ESC', 'PLA', 'PUE']
    
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
    
    def process_xml(self, xml_path: Path, seen_keys: set) -> List[Dict[str, str]]:
        """Processa un fitxer XML i extreu totes les BIE."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        bie_elements = root.findall('.//BIE')
        results = []
        for bie in bie_elements:
            record = process_bie_element(bie)
            composite_key = record['RC']
            if composite_key in seen_keys:
                continue
            seen_keys.add(composite_key)
            results.append(record)
        return results
    
    def export(self) -> int:
        """Exporta les dades a CSV."""
        self.temp_dir = Path(tempfile.mkdtemp())
        try:
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
            
            seen_keys = set()
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
                        data = self.process_xml(xml_file, seen_keys)
                        all_data.extend(data)
                        progress.update(task, advance=1)
            else:
                for xml_file in xml_files:
                    data = self.process_xml(xml_file, seen_keys)
                    all_data.extend(data)
            
            if self.verbose:
                console.print(f"[cyan]💾 Guardant CSV:[/cyan] {self.output_file}")
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_ALL)
                writer.writerow(self.FIELDS)
                for record in all_data:
                    row = [
                        record['TV'],
                        record['NV'],
                        record['PNP'],
                        record['PLP'],
                        record['BQ'],
                        record['ES'],
                        record['PT'],
                        record['PU'],
                        record['RC'],
                        record['PCA'],
                        record['CAR'],
                        record['CDC1'],
                        record['CDC2'],
                        record['CPO'],
                        record['CPA'],
                        record['KM'],
                        record['ESC'],
                        record['PLA'],
                        record['PUE']
                    ]
                    writer.writerow(row)
            
            if self.verbose:
                console.print(f"[green]✓ Exportades {len(all_data)} files[/green]")
            return 0
        finally:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
