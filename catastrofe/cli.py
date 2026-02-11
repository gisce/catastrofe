#!/usr/bin/env python3
"""
Catastrofe CLI - Eina per processar dades del Cadastre
"""

import click
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.text import Text

from catastrofe.xml_splitter import XMLSplitter

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🏛️ Catastrofe - Eina per processar dades del Cadastre
    
    Utilitza els subcomandos per processar fitxers XML del Cadastre.
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '-o', '--output-dir',
    type=click.Path(path_type=Path),
    default=Path('output'),
    help='Directori de sortida (per defecte: output)'
)
@click.option(
    '-s', '--max-size',
    type=int,
    default=450,
    help='Mida màxima per fitxer en KB (per defecte: 450)'
)
def split(input_file, output_dir, max_size):
    """
    Divideix un fitxer XML gran en parts més petites.
    
    Exemple:
        catastrofe split girona_entrada.xml
        catastrofe split girona_entrada.xml -o resultats -s 400
    """
    # Banner inicial
    console.print()
    banner = Panel(
        Text.from_markup(
            f"[bold cyan]🔪 XML Splitter[/bold cyan]\n"
            f"Dividint fitxers XML grans amb estil ✨"
        ),
        border_style="cyan",
        box=box.DOUBLE
    )
    console.print(banner)
    console.print()
    
    try:
        splitter = XMLSplitter(
            input_file=input_file,
            output_dir=output_dir,
            max_size_kb=max_size
        )
        
        output_files = splitter.split()
        splitter.display_summary(output_files)
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}", style="red")
        console.print_exception()
        raise click.Abort()


if __name__ == '__main__':
    cli()
