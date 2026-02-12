# 🏛️ Catastrofe

Eina per processar dades del Cadastre espanyol. Inclou utilitats per dividir fitxers XML grans i exportar dades a CSV.

## ✨ Característiques

### Split - Divisor de fitxers XML

- 🎯 **Divisió intel·ligent**: Divideix fitxers XML mantenint l'estructura jeràrquica
- 📊 **Interfície visual**: Utilitza [Rich](https://github.com/Textualize/rich) per una experiència d'usuari espectacular
- ⚡ **Ràpid i eficient**: Processa fitxers grans amb barra de progrés en temps real
- 🎨 **Output colorejat**: Taules boniques amb estadístiques detallades
- 🔧 **Configurable**: Mida màxima personalitzable per cada part

### Export CSV - Exportador de dades cadastrals

- 📄 **Múltiples formats**: Accepta fitxers .zip i .xml com a entrada
- 📊 **Unificació de dades**: Combina múltiples fitxers en un únic CSV
- 🔢 **Preservació de zeros**: Manté els zeros inicials dels camps numèrics
- 📋 **Camps detallats**: Extreu tots els camps importants del cadastre
- ⚡ **Processament batch**: Processa múltiples fitxers d'una sola vegada

## 📋 Requisits

- Python 3.11+
- Rich library
- Click library

## 🚀 Instal·lació

### Des de codi font

```bash
# Clona el repositori
git clone <repository-url>
cd catastrofe

# Instal·la el paquet (mode desenvolupament)
pip install -e .
```

Això crearà automàticament el comando `catastrofe` al teu PATH.

### Binari precompilat (Linux)

Descarrega el binari des de [GitHub Releases](https://github.com/YOUR_USER/catastrofe/releases):

```bash
# Descarrega el binari
wget https://github.com/YOUR_USER/catastrofe/releases/latest/download/catastrofe

# Fes-lo executable
chmod +x catastrofe

# Mou-lo al PATH
sudo mv catastrofe /usr/local/bin/catastrofe
```

## 💻 Ús

### Comando principal

```bash
catastrofe --help
```

### Split - Dividir fitxers XML

Divideix fitxers XML grans en parts més petites.

```bash
# Ús bàsic
catastrofe split girona_entrada.xml

# Especifica el directori de sortida
catastrofe split girona_entrada.xml -o resultats

# Canvia la mida màxima per fitxer (en KB)
catastrofe split girona_entrada.xml -s 400

# Combina opcions
catastrofe split girona_entrada.xml -o sortida -s 500
```

### Export CSV - Exportar dades a CSV

Exporta dades del Cadastre a format CSV. Accepta fitxers .zip o .xml com a entrada.

```bash
# Exporta un fitxer
catastrofe export-csv dades.zip -o sortida.csv

# Exporta múltiples fitxers (es combinen en un sol CSV)
catastrofe export-csv file1.zip file2.xml file3.zip -o sortida.csv

# El CSV generat conté els següents camps separats per ;
# TV, NV, PNP, PLP, BQ, ES, PT, PU, PCA+CAR+CDC1+CDC2, PCA, CAR, CDC1, CDC2,
# CPO, CPA, KM, ESC, PLA, PUE, POL, PAR, SNP, SLP, KK
```

**Nota:** Els valors es mantenen com a text per preservar els zeros inicials (ex: 0005).

## 📁 Estructura del projecte

```
catastrofe/
├── catastrofe/             # Paquet principal
│   ├── __init__.py         # Exporta classes
│   ├── xml_splitter.py     # Classe XMLSplitter
│   ├── csv_exporter.py     # Classe CatastroCSVExporter
│   └── cli.py              # CLI amb Click
├── output/                 # Fitxers de sortida (generats automàticament)
├── girona_entrada.xml      # Fitxer d'exemple d'entrada
├── pyproject.toml          # Configuració del paquet
├── requirements.txt        # Dependències de Python
└── README.md               # Aquesta documentació
```

## 📚 Ús com a biblioteca

El paquet es pot utilitzar com a biblioteca Python en altres projectes:

### XMLSplitter - Dividir XMLs

```python
from pathlib import Path
from catastrofe import XMLSplitter

# Divideix un fitxer XML
splitter = XMLSplitter(
    input_file=Path("dades.xml"),
    output_dir=Path("sortida"),
    max_size_kb=450,
    verbose=False  # Sense sortida visual
)
output_files = splitter.split()

# output_files és una llista de Path amb els fitxers generats
for file in output_files:
    print(f"Generat: {file}")
```

### CatastroCSVExporter - Exportar a CSV

```python
from pathlib import Path
from catastrofe import CatastroCSVExporter

# Exporta dades a CSV
exporter = CatastroCSVExporter(
    input_files=[Path("file1.zip"), Path("file2.xml")],
    output_file=Path("sortida.csv"),
    verbose=False  # Sense sortida visual
)
exporter.export()
```

Consulta `exemple_us_llibreria.py` per a més exemples d'ús.

## 🎯 Com funciona

1. **Llegeix** el fitxer XML d'entrada
2. **Analitza** l'estructura i identifica els elements repetitius (elements `<DAT>`)
3. **Divideix** els elements en grups que no superin la mida màxima especificada
4. **Manté** l'estructura base XML (capçaleres, namespaces, elements globals)
5. **Genera** múltiples fitxers XML vàlids amb nomenclatura seqüencial

### Exemple d'estructura XML suportada

```xml
<?xml version="1.0" encoding="utf-8"?>
<LISTADATOS xmlns="http://www.catastro.meh.es/">
  <FEC>2026-02-06</FEC>
  <FIN/>
  <DAT>
    <RC>000100100DG84D</RC>
    <PRO>17</PRO>
    <MUN>79</MUN>
  </DAT>
  <DAT>
    <!-- Més elements DAT... -->
  </DAT>
</LISTADATOS>
```

L'eina preserva els elements `<FEC>` i `<FIN>` en cada fitxer generat, i distribueix els elements `<DAT>` entre els diferents fitxers de sortida.

## 📊 Sortida

L'eina mostra:

- 📂 Informació del fitxer d'entrada
- ✓ Nombre total d'elements trobats
- 📈 Barra de progrés amb temps transcorregut
- 📊 Taula resum amb:
  - Nom de cada fitxer generat
  - Mida en KB (amb color segons si està dins del límit)
  - Nombre d'elements per fitxer
  - Totals acumulats

### Exemple de sortida

```
╔══════════════════════════════════════════════════════════╗
║           🔪 XML Splitter                                ║
║   Dividint fitxers XML grans amb estil ✨                ║
╚══════════════════════════════════════════════════════════╝

📂 Llegint fitxer: girona_entrada.xml
✓ Elements DAT trobats: 12120

⠋ Processant elements... ━━━━━━━━━━━━━━━ 100% • 12120/12120 elements

            📊 Resum de fitxers generats            
╭────────────────────────────┬──────────┬───────────────╮
│ Fitxer                     │     Mida │ Elements DAT  │
├────────────────────────────┼──────────┼───────────────┤
│ girona_entrada_part_001.xml│  449.2 KB│          7500 │
│ girona_entrada_part_002.xml│  422.8 KB│          4620 │
├────────────────────────────┼──────────┼───────────────┤
│ TOTAL: 2 fitxers           │  872.0 KB│         12120 │
╰────────────────────────────┴──────────┴───────────────╯

╭─────────────── Completat! ───────────────╮
│ ✓ Fitxers guardats a: /path/to/output    │
╰──────────────────────────────────────────╯
```

## 🎨 Per què és "cool"?

- 🌈 **Colors i emojis**: Interfície visual atractiva
- 📊 **Taules boniques**: Amb Rich, les dades es presenten de forma elegant
- ⏱️ **Progrés en temps real**: Saps exactament què està passant
- ✨ **Experiència professional**: No és només un script, és una eina amb personalitat

## 🤝 Contribucions

Les contribucions són benvingudes! Si tens idees per millorar l'eina:

1. Fork el projecte
2. Crea una branca per la teva feature (`git checkout -b feature/AmazingFeature`)
3. Commit els canvis (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branca (`git push origin feature/AmazingFeature`)
5. Obre un Pull Request

## 📝 Llicència

Aquest projecte és de codi obert i està disponible sota llicència MIT.

## 👨‍💻 Autor

Creat amb ❤️ i Python

## 🐛 Problemes coneguts / Limitacions

- El càlcul de mida és aproximat i pot variar lleugerament del fitxer final
- Assumeix que els elements repetitius són `<DAT>`
- No valida l'esquema XML contra un XSD

## 🔮 Futures millores

- [ ] Suport per altres estructures XML
- [ ] Validació XML Schema (XSD)
- [ ] Compressió automàtica dels fitxers de sortida
- [ ] Mode batch per processar múltiples fitxers
- [ ] Export de logs en format JSON

---

**Gaudeix dividint XMLs amb estil! 🎉**
