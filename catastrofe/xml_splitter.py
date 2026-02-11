#!/usr/bin/env python3
"""
XML Splitter - Divideix fitxers XML grans en parts més petites
mantenint l'estructura original.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich import box

console = Console()

class XMLSplitter:
    """Classe per dividir fitxers XML grans en parts més petites."""
    
    def __init__(self, input_file: Path, output_dir: Path, max_size_kb: int = 450, verbose: bool = True):
        """
        Inicialitza el divisor de fitxers XML.
        
        Args:
            input_file: Path al fitxer XML d'entrada
            output_dir: Directori on guardar els fitxers de sortida
            max_size_kb: Mida màxima per fitxer en KB (per defecte: 450)
            verbose: Si és True, mostra missatges de progrés (per defecte: True)
        """
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.max_size_bytes = max_size_kb * 1024
        self.namespace = {"": "http://www.catastro.meh.es/"}
        self.verbose = verbose
        
    def parse_xml(self) -> ET.ElementTree:
        """Llegeix el fitxer XML d'entrada."""
        if self.verbose:
            console.print(f"[cyan]📂 Llegint fitxer:[/cyan] {self.input_file}")
        tree = ET.parse(self.input_file)
        return tree
    
    def estimate_element_size(self, element: ET.Element) -> int:
        """
        Estima la mida en bytes d'un element XML amb indentació.
        Calcula aproximadament afegint overhead per indentació.
        """
        # Mida base sense indentació
        base_size = len(ET.tostring(element, encoding='utf-8'))
        
        # Estima overhead d'indentació (aproximadament 2 espais per nivell * nombre de tags)
        # Comptant tags dins l'element
        num_children = len(list(element.iter()))
        indent_overhead = num_children * 4  # ~2 espais entrada + 2 sortida aprox
        
        return base_size + indent_overhead
    
    def create_base_structure(self, root: ET.Element) -> ET.Element:
        """Crea l'estructura base per cada fitxer de sortida."""
        new_root = ET.Element(root.tag, attrib=root.attrib)
        
        # Copia elements que no són DAT (com FEC, FIN)
        for child in root:
            if not child.tag.endswith('DAT'):
                new_root.append(child)
        
        return new_root
    
    def split(self) -> List[Path]:
        """
        Divideix el fitxer XML en múltiples parts.
        
        Returns:
            Llista amb els Paths dels fitxers generats
        """
        tree = self.parse_xml()
        root = tree.getroot()
        
        # Troba tots els elements DAT
        dat_elements = [elem for elem in root if elem.tag.endswith('DAT')]
        total_elements = len(dat_elements)
        
        if self.verbose:
            console.print(f"[green]✓ Elements DAT trobats:[/green] {total_elements}")
        
        # Assegura que el directori de sortida existeix
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        output_files = []
        current_part = 1
        current_root = self.create_base_structure(root)
        current_size = self.estimate_element_size(current_root)
        
        # Capçalera XML (aproximada)
        header_overhead = 100  # Bytes per capçalera XML + salts de línia finals
        
        if self.verbose:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("•"),
                TextColumn("{task.completed}/{task.total} elements"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                
                task = progress.add_task(
                    "[cyan]Processant elements...", 
                    total=total_elements
                )
                
                for dat_element in dat_elements:
                    element_size = self.estimate_element_size(dat_element)
                    
                    # Comprova si afegir aquest element superaria la mida màxima
                    if current_size + element_size + header_overhead > self.max_size_bytes and len(current_root) > 2:
                        # Guarda el fitxer actual
                        output_file = self.save_part(current_root, current_part)
                        output_files.append(output_file)
                        
                        # Inicia una nova part
                        current_part += 1
                        current_root = self.create_base_structure(root)
                        current_size = self.estimate_element_size(current_root)
                    
                    # Afegeix l'element a la part actual
                    current_root.append(dat_element)
                    current_size += element_size
                    
                    progress.update(task, advance=1)
        else:
            # Mode silenciós (per a ús com a biblioteca)
            for dat_element in dat_elements:
                element_size = self.estimate_element_size(dat_element)
                
                # Comprova si afegir aquest element superaria la mida màxima
                if current_size + element_size + header_overhead > self.max_size_bytes and len(current_root) > 2:
                    # Guarda el fitxer actual
                    output_file = self.save_part(current_root, current_part)
                    output_files.append(output_file)
                    
                    # Inicia una nova part
                    current_part += 1
                    current_root = self.create_base_structure(root)
                    current_size = self.estimate_element_size(current_root)
                
                # Afegeix l'element a la part actual
                current_root.append(dat_element)
                current_size += element_size
        
        # Guarda l'última part
        if len(current_root) > 2:  # Té elements DAT (més enllà de FEC i FIN)
            output_file = self.save_part(current_root, current_part)
            output_files.append(output_file)
        
        return output_files
    
    def save_part(self, root: ET.Element, part_number: int) -> Path:
        """Guarda una part del XML."""
        output_file = self.output_dir / f"{self.input_file.stem}_part_{part_number:03d}.xml"
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(
            output_file,
            encoding='utf-8',
            xml_declaration=True
        )
        
        actual_size = output_file.stat().st_size
        size_kb = actual_size / 1024
        
        return output_file
    
    def display_summary(self, output_files: List[Path]):
        """Mostra un resum dels fitxers generats."""
        console.print()
        
        table = Table(
            title="📊 Resum de fitxers generats",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("Fitxer", style="cyan", no_wrap=True)
        table.add_column("Mida", justify="right", style="green")
        table.add_column("Elements DAT", justify="right", style="yellow")
        
        total_size = 0
        total_elements = 0
        
        for output_file in output_files:
            size = output_file.stat().st_size
            total_size += size
            
            # Compta els elements DAT
            tree = ET.parse(output_file)
            root = tree.getroot()
            num_elements = len([e for e in root if e.tag.endswith('DAT')])
            total_elements += num_elements
            
            size_kb = size / 1024
            color = "green" if size_kb <= 450 else "yellow" if size_kb <= 500 else "red"
            
            table.add_row(
                output_file.name,
                f"[{color}]{size_kb:.1f} KB[/{color}]",
                str(num_elements)
            )
        
        table.add_section()
        table.add_row(
            f"[bold]TOTAL: {len(output_files)} fitxers[/bold]",
            f"[bold]{total_size/1024:.1f} KB[/bold]",
            f"[bold]{total_elements}[/bold]"
        )
        
        console.print(table)
        console.print()
        
        # Missatge final
        from rich.panel import Panel
        panel = Panel(
            f"[green]✓ Fitxers guardats a:[/green] [cyan]{self.output_dir.absolute()}[/cyan]",
            title="[bold green]Completat![/bold green]",
            border_style="green"
        )
        console.print(panel)

