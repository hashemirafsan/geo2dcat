# geo2dcat

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-green)](docker-compose.yml)

A Python library and CLI tool for converting geospatial and scientific datasets into **DCAT 3 JSON-LD** with automatic CF Convention ontology mappings. Transform NetCDF, GeoTIFF, Shapefile, GRIB, HDF5, and CSV files into standardized metadata for EU Dataspace, INSPIRE, and EOSC publishing.

## Features

- **Multi-format support**: NetCDF, GeoTIFF/Raster, Shapefile/Vector, GRIB, HDF5, CSV
- **Automatic metadata extraction**: CF conventions, spatial/temporal bounds, variables
- **Ontology mapping**: SWEET, ENVO, and INSPIRE theme mappings for 100+ CF standard names
- **Batch processing**: Convert entire directories with pattern matching
- **SHACL generation**: Auto-generate validation shapes from dataset collections
- **Docker-ready**: GDAL/PROJ/GEOS pre-configured environment
- **Extensible**: Plugin architecture for new formats and mappings
- **DLLM training**: Synthetic data generator for fine-tuning domain language models

## Quick Start

### Installation

```bash
# Core package (NetCDF support only)
pip install geo2dcat

# Install with specific format support
pip install geo2dcat[geotiff]      # GeoTIFF/Raster support
pip install geo2dcat[shapefile]    # Shapefile/Vector support
pip install geo2dcat[grib]         # GRIB/GRIB2 support
pip install geo2dcat[hdf5]         # HDF5 support
pip install geo2dcat[csv]          # CSV/TSV support

# Install with all formats
pip install geo2dcat[all]
```

### Basic Usage

#### Python API

```python
from geo2dcat import convert, convert_to_file, batch_convert

# Convert a single file to DCAT JSON-LD
dcat_metadata = convert("temperature_data.nc")

# Save to file
output_path = convert_to_file("temperature_data.nc", "output.jsonld")

# Batch convert a directory
results = batch_convert("./data/", pattern="**/*.nc")
```

#### Command Line

```bash
# Convert single file
geo2dcat convert temperature_data.nc

# Convert with custom dataset URI
geo2dcat convert data.nc --id "https://myorg.eu/datasets/temp-2024"

# Batch convert directory
geo2dcat batch ./data/ --output catalog.jsonld

# Generate SHACL shapes
geo2dcat shacl ./data/ --output shapes.ttl
```

## Docker Environment

### Prerequisites

- Docker and Docker Compose installed
- `.env` file with `ANTHROPIC_API_KEY` (for synthetic generation only)

### Quick Start with Docker

```bash
# Build the Docker image
docker compose build geo2dcat

# Generate test fixtures
docker compose run --rm geo2dcat python tests/fixtures/generate.py

# Run tests
make test

# Interactive shell
make shell

# Inside container
geo2dcat convert /data/your_file.nc
geo2dcat batch /data/ --output /outputs/catalog.jsonld
```

### Available Make Commands

| Command | Description |
|---------|------------|
| `make build` | Build Docker image |
| `make shell` | Interactive bash shell in container |
| `make test` | Run full test suite with coverage |
| `make generate-fixtures` | Generate sample test files |
| `make sparql` | Start Apache Jena Fuseki SPARQL endpoint |
| `make jupyter` | Start Jupyter notebook server |
| `make convert FILE=x.nc` | Convert single file |
| `make batch` | Batch convert `/data/` directory |
| `make shacl` | Generate SHACL shapes |
| `make clean` | Remove containers and images |

## Supported Formats

| Format | Extensions | Required Package |
|--------|------------|-----------------|
| NetCDF | `.nc`, `.nc4`, `.netcdf` | `netCDF4` |
| GeoTIFF/Raster | `.tif`, `.tiff`, `.img` | `rasterio` |
| Shapefile/Vector | `.shp`, `.geojson`, `.gpkg` | `geopandas`, `fiona` |
| GRIB/GRIB2 | `.grib`, `.grib2`, `.grb` | `cfgrib`, `xarray` |
| HDF5 | `.h5`, `.hdf5`, `.he5` | `h5py` |
| CSV/TSV | `.csv`, `.tsv` | `pandas` |

## Output Format

geo2dcat produces DCAT 3 compliant JSON-LD with CF Convention extensions:

```json
{
  "@context": {
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "sweet": "http://sweetontology.net/repr#",
    "theme": "http://inspire.ec.europa.eu/theme/",
    "cf": "http://cfconventions.org/cf-conventions/"
  },
  "@type": "dcat:Dataset",
  "@id": "urn:dataset:temperature-era5-2024",
  "dct:title": {
    "@value": "ERA5 Temperature Reanalysis",
    "@language": "en"
  },
  "dcat:theme": [
    {"@id": "theme:AtmosphericConditions"}
  ],
  "cf:variableMappings": [
    {
      "cf:variableName": "t2m",
      "cf:standardName": "air_temperature",
      "cf:units": "K",
      "cf:ontologyURI": "sweet:AirTemperature",
      "cf:dimensions": ["time", "latitude", "longitude"],
      "cf:shape": [8760, 721, 1440]
    }
  ],
  "dct:spatial": {
    "@type": "dct:Location",
    "geo:asWKT": {
      "@type": "geo:wktLiteral",
      "@value": "POLYGON((-180 -90, 180 -90, 180 90, -180 90, -180 -90))"
    }
  },
  "dct:temporal": {
    "@type": "dct:PeriodOfTime",
    "dcat:startDate": {"@value": "2024-01-01T00:00:00Z"},
    "dcat:endDate": {"@value": "2024-12-31T23:59:59Z"}
  }
}
```

## CLI Commands

### Convert Commands

```bash
# Convert single file
geo2dcat convert input.nc
geo2dcat convert input.nc --output metadata.jsonld
geo2dcat convert input.nc --id "https://mydata.eu/dataset/123"

# Show only variable mappings
geo2dcat convert input.nc --variables-only

# Output as RDF Turtle (requires rdflib)
geo2dcat convert input.nc --format turtle
```

### Batch Processing

```bash
# Process all files in directory
geo2dcat batch ./data/

# Filter by pattern
geo2dcat batch ./data/ --pattern "**/*.nc"
geo2dcat batch ./data/ --pattern "**/ERA5*.nc" --output era5_catalog.jsonld
```

### SHACL Shape Generation

```bash
# Generate validation shapes from dataset collection
geo2dcat shacl ./data/ --output shapes.ttl
geo2dcat shacl ./data/ --shape-name ClimateDatasetShape
```

### Metadata Lookup

```bash
# Lookup CF standard name mappings
geo2dcat lookup t2m
geo2dcat lookup air_temperature

# List all supported formats
geo2dcat formats
```

### Synthetic Data Generation

Generate training data for Domain LLMs:

```bash
geo2dcat synthetic \
  --seed-dir ./dcat_outputs/ \
  --augment 2000 \
  --templates 3000 \
  --claude 1000 \
  --output training_data.jsonl \
  --api-key $ANTHROPIC_API_KEY
```

## API Documentation

### Core Functions

#### `convert(filepath, dataset_id=None)`

Convert a single file to DCAT JSON-LD.

**Parameters:**
- `filepath` (str): Path to input file
- `dataset_id` (str, optional): Custom dataset URI

**Returns:**
- `dict`: DCAT JSON-LD metadata

**Example:**
```python
from geo2dcat import convert

metadata = convert("temperature.nc")
metadata = convert("elevation.tif", dataset_id="https://data.eu/dem-alps")
```

#### `batch_convert(directory, pattern=None)`

Process multiple files in a directory.

**Parameters:**
- `directory` (str): Directory path to scan
- `pattern` (str, optional): Glob pattern filter

**Returns:**
- `list[dict]`: Results with status and metadata

**Example:**
```python
from geo2dcat import batch_convert

results = batch_convert("./climate_data/")
for result in results:
    if result["status"] == "ok":
        print(f"Converted: {result['file']}")
    else:
        print(f"Error in {result['file']}: {result['error']}")
```

### Advanced Features

#### Custom Mappings

Extend CF standard name mappings:

```python
from geo2dcat.mappings import CF_STANDARD_NAME_MAPPING

# Add custom mapping
CF_STANDARD_NAME_MAPPING["custom_temperature"] = "sweet:CustomTemp"
```

#### SHACL Validation

Generate and use SHACL shapes:

```python
from geo2dcat.shacl_generator import generate_shacl

# Generate shapes from DCAT outputs
shapes = generate_shacl(
    dcat_outputs=metadata_list,
    shape_name="MyDatasetShape",
    output_path="validation.ttl"
)
```

## CF Convention Mappings

geo2dcat includes comprehensive mappings for:

### Atmospheric Variables
- `air_temperature` → `sweet:AirTemperature`
- `precipitation_flux` → `sweet:Precipitation`
- `wind_speed` → `sweet:WindSpeed`
- `air_pressure` → `sweet:AtmosphericPressure`
- `relative_humidity` → `sweet:RelativeHumidity`

### Ocean Variables
- `sea_water_temperature` → `sweet:SeaWaterTemperature`
- `sea_water_salinity` → `sweet:Salinity`
- `sea_surface_height` → `sweet:SeaSurfaceHeight`

### Land Surface Variables
- `soil_moisture_content` → `sweet:SoilMoisture`
- `normalized_difference_vegetation_index` → `envo:NDVI`
- `leaf_area_index` → `envo:LeafAreaIndex`

### Common Aliases (ERA5, CMIP6, CORDEX)
- `t2m`, `tas` → `air_temperature`
- `pr`, `tp` → `precipitation_flux`
- `u10`, `uas` → `eastward_wind`
- `sst`, `tos` → `sea_surface_temperature`

See [full mapping documentation](docs/mappings.md) for complete list.

## Architecture

```
geo2dcat/
├── extractors/          # Format-specific metadata extractors
│   ├── netcdf.py       # NetCDF/NC4 support
│   ├── geotiff.py      # GeoTIFF/Raster support
│   ├── shapefile.py    # Vector format support
│   ├── grib.py         # GRIB/GRIB2 support
│   ├── hdf5.py         # HDF5 support
│   └── csv.py          # CSV/TSV support
├── mappings/           # Ontology and theme mappings
│   ├── cf_standard_names.py  # CF → SWEET/ENVO URIs
│   ├── cf_short_aliases.py   # Common variable aliases
│   └── themes.py             # INSPIRE theme mappings
├── dcat_builder.py     # DCAT 3 JSON-LD construction
├── shacl_generator.py  # SHACL shape generation
├── synthetic/          # Training data generation
│   ├── generator.py    # Main generator class
│   ├── augmentor.py    # Data augmentation
│   ├── templates.py    # Template-based generation
│   └── hard_cases.py   # Claude API integration
└── cli.py             # Command-line interface
```

## Development

### Running Tests

```bash
# Using Docker (recommended)
make test

# Or directly with pytest
pytest tests/ -v --cov=geo2dcat

# Test specific format
pytest tests/test_netcdf.py -v
```

### Adding New Format Support

1. Create extractor in `geo2dcat/extractors/myformat.py`
2. Implement `extract_myformat()` returning `NormalizedMetadata`
3. Register in `geo2dcat/extractors/__init__.py`
4. Add tests in `tests/test_myformat.py`

Example extractor:

```python
from geo2dcat.types import NormalizedMetadata, VariableInfo

def extract_myformat(filepath: str) -> NormalizedMetadata:
    # Open and read metadata
    with open(filepath, 'rb') as f:
        # Extract metadata...
        pass
    
    return {
        "format": "MyFormat",
        "title": title,
        "variables": variables,
        # ... other fields
    }
```

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing`)
5. Open Pull Request

## Troubleshooting

### Common Issues

**ImportError: libgdal.so not found**
- Use the Docker environment or install GDAL system libraries
- Ubuntu/Debian: `apt-get install gdal-bin libgdal-dev`
- macOS: `brew install gdal`

**cfgrib fails to open GRIB files**
- Install eccodes system library
- Ubuntu/Debian: `apt-get install libeccodes-dev`
- macOS: `brew install eccodes`

**netCDF4 installation fails**
- Install HDF5 and NetCDF libraries
- Ubuntu/Debian: `apt-get install libhdf5-dev libnetcdf-dev`
- macOS: `brew install hdf5 netcdf`

### Docker Troubleshooting

If you encounter issues with the Docker environment:

```bash
# Clean and rebuild
make clean
make build

# Check logs
docker compose logs geo2dcat

# Run with verbose output
docker compose run --rm geo2dcat geo2dcat convert /data/test.nc --debug
```

## Real-World Examples

### Climate Data Processing

```python
from geo2dcat import batch_convert
import json

# Convert ERA5 reanalysis data
results = batch_convert("./era5_data/", pattern="**/era5_*.nc")

# Combine into catalog
catalog = {
    "@context": {"@import": "https://w3id.org/dcat/context.jsonld"},
    "@type": "dcat:Catalog",
    "dcat:dataset": [r["dcat"] for r in results if r["status"] == "ok"]
}

# Save catalog
with open("era5_catalog.jsonld", "w") as f:
    json.dump(catalog, f, indent=2)
```

### Integration with CKAN

```python
from geo2dcat import convert
import ckanapi

# Convert file
metadata = convert("temperature_2024.nc")

# Push to CKAN
ckan = ckanapi.RemoteCKAN('https://data.europa.eu')
package = ckan.action.package_create(
    name=metadata["@id"],
    title=metadata["dct:title"]["@value"],
    notes=metadata.get("dct:description", {}).get("@value", ""),
    extras=[
        {"key": "dcat_metadata", "value": json.dumps(metadata)},
        {"key": "cf_conventions", "value": "CF-1.8"}
    ]
)
```

## Performance

- **Memory efficient**: Metadata-only extraction, no data loading
- **Parallel processing**: Batch operations use multiprocessing
- **Large file support**: Handles multi-GB NetCDF/GRIB files
- **Caching**: Reuses ontology mappings across conversions

Benchmarks on typical datasets:
- NetCDF (1GB): ~0.5s
- GeoTIFF (500MB): ~0.3s
- Shapefile (100MB): ~0.2s
- GRIB2 (2GB): ~1.2s

## Roadmap

- [ ] Support for Zarr format
- [ ] STAC (SpatioTemporal Asset Catalog) output
- [ ] OGC API - Records integration
- [ ] Validation against DCAT-AP profiles
- [ ] Web service API
- [ ] GUI for interactive conversion

## Citation

If you use geo2dcat in your research, please cite:

```bibtex
@software{geo2dcat2024,
  title = {geo2dcat: Geospatial to DCAT Metadata Converter},
  year = {2024},
  url = {https://github.com/yourusername/geo2dcat}
}
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- CF Conventions community for standard name tables
- SWEET ontology for scientific concept URIs
- INSPIRE directive for spatial data themes
- OSGeo for GDAL/OGR geospatial libraries

## Support

- Issues: [GitHub Issues](https://github.com/yourusername/geo2dcat/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/geo2dcat/discussions)
- Email: support@geo2dcat.org