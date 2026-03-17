# geo2dcat — Requirements & Specification

---

## Docker Environment & Testing

### Prerequisites

- Docker + Docker Compose installed
- `.env` file with `ANTHROPIC_API_KEY=...` (only needed for synthetic generation)

### Project layout expected by Docker

```
geo2dcat/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements-dev.txt
├── pyproject.toml
├── .env                     # copy from .env.example
├── geo2dcat/              # package source
├── tests/
│   └── fixtures/
│       └── generate.py      # run this first to create sample files
├── data/                    # put your real NetCDF/GeoTIFF files here
└── outputs/                 # DCAT outputs written here
```

### Step 1 — Build the image

```bash
docker compose build geo2dcat
```

Base image is `ghcr.io/osgeo/gdal:ubuntu-small-3.8.4`.
GDAL, PROJ, GEOS, HDF5, NetCDF, eccodes are all pre-installed at OS level.
Python packages installed from `requirements-dev.txt`.

### Step 2 — Generate test fixtures

Creates minimal sample files (`.nc`, `.tif`, `.shp`, `.csv`, `.h5`) under `tests/fixtures/`:

```bash
docker compose run --rm geo2dcat python tests/fixtures/generate.py
```

For GRIB testing, download a real GRIB2 file from ECMWF open data and put it at `tests/fixtures/sample.grib2`.

### Step 3 — Run tests

```bash
# All tests with coverage
docker compose --profile test run --rm test

# Or via Makefile shortcut
make test

# Single test file
docker compose run --rm geo2dcat pytest tests/test_netcdf.py -v

# Single test function
docker compose run --rm geo2dcat pytest tests/test_netcdf.py::test_convert_basic -v
```

### Step 4 — Interactive dev shell

```bash
make shell
# or
docker compose run --rm geo2dcat bash

# Inside container:
geo2dcat convert /data/your_file.nc
geo2dcat batch /data/ --output /outputs/catalog.jsonld
geo2dcat shacl /data/ --output /outputs/shapes.shacl.ttl
```

### Step 5 — SPARQL triplestore (optional)

```bash
make sparql
# Fuseki available at http://localhost:3030
# Dataset: /climate-kg
# Credentials: admin / admin123
```

Load DCAT output into Fuseki:
```bash
docker compose run --rm geo2dcat python - <<'EOF'
from rdflib import Graph
import json, requests

with open("/outputs/catalog.jsonld") as f:
    data = json.load(f)

g = Graph()
g.parse(data=json.dumps(data), format="json-ld")
turtle = g.serialize(format="turtle")

requests.post(
    "http://fuseki:3030/climate-kg/data",
    data=turtle.encode(),
    headers={"Content-Type": "text/turtle"}
)
print(f"Loaded {len(g)} triples")
EOF
```

### Makefile commands reference

| Command | What it does |
|---------|-------------|
| `make build` | Build Docker image |
| `make shell` | Interactive bash inside container |
| `make test` | Run full test suite with coverage |
| `make generate-fixtures` | Generate sample test files |
| `make sparql` | Start Fuseki at localhost:3030 |
| `make sparql-stop` | Stop Fuseki |
| `make jupyter` | Start Jupyter at localhost:8888 |
| `make convert FILE=x.nc` | Quick convert single file |
| `make batch` | Batch convert all files in `/data/` |
| `make shacl` | Generate SHACL from `/data/` |
| `make clean` | Remove containers + images |

### requirements-dev.txt contents

```
numpy>=1.24.0
pandas>=2.0.0
xarray>=2023.1.0
rasterio>=1.3.0
geopandas>=0.13.0
fiona>=1.9.0
pyproj>=3.5.0
shapely>=2.0.0
netCDF4>=1.6.0
h5py>=3.8.0
cfgrib>=0.9.10
eccodes>=1.6.0
rdflib>=6.3.0
pyoxigraph>=0.3.0
anthropic>=0.25.0
pytest>=7.0
pytest-cov>=4.0
pytest-asyncio>=0.21.0
ruff>=0.1.0
mypy>=1.0.0
```

### Dockerfile summary

```dockerfile
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.4

# System: libeccodes-dev, libhdf5-dev, libnetcdf-dev,
#         libgeos-dev, libproj-dev, libspatialindex-dev
# Then: pip install -r requirements-dev.txt
# Then: pip install -e ".[all]"
```

Install Python packages with `--break-system-packages` flag because the GDAL base image uses system Python.

### Common issues

**ImportError: libgdal.so not found**
→ Always use the GDAL base image, never install GDAL via pip directly.

**cfgrib fails to open GRIB**
→ `eccodes` must be installed at OS level (`libeccodes-dev`), not just via pip.

**rasterio CRS errors**
→ `PROJ_LIB` env var is pre-set in the GDAL image. Do not override it.

**netCDF4 install fails**
→ `libnetcdf-dev` and `libhdf5-dev` must be present before pip install.

---

## Overview

`geo2dcat` is a Python library and CLI tool that converts geospatial and scientific file formats into **DCAT 3 JSON-LD** with automatic ontology mappings.

The tool serves two purposes:
1. **Standalone utility** — researchers convert their datasets to DCAT 3 for EU Dataspace / EOSC publishing
2. **Synthetic training data generator** — generates labeled input→output pairs for fine-tuning a Domain LLM (DLLM) that handles ambiguous/incomplete metadata the rule-based system cannot resolve

---

## Package Structure

```
geo2dcat/
├── __init__.py              # Public API: convert(), convert_to_file(), batch_convert()
├── extractors/
│   ├── __init__.py          # extract(filepath) → normalized dict
│   ├── netcdf.py            # NetCDF / NC4 extractor
│   ├── geotiff.py           # GeoTIFF / Raster extractor
│   ├── shapefile.py         # Shapefile / GeoJSON / GeoPackage extractor
│   ├── grib.py              # GRIB / GRIB2 extractor
│   ├── hdf5.py              # HDF5 extractor
│   └── csv.py               # CSV / TSV extractor
├── mappings/
│   ├── __init__.py
│   ├── cf_standard_names.py # CF standard name → SWEET/ENVO ontology URI
│   ├── cf_short_aliases.py  # ERA5/CMIP6 short names → CF standard names
│   └── themes.py            # ontology URI → dcat:theme
├── dcat_builder.py          # normalized dict → DCAT 3 JSON-LD
├── shacl_generator.py       # batch DCAT outputs → SHACL shapes
├── synthetic/
│   ├── __init__.py
│   ├── generator.py         # SyntheticGenerator class
│   ├── augmentor.py         # Augmentation strategies on real pairs
│   ├── templates.py         # Template-based pair generation
│   └── hard_cases.py        # Claude API — ambiguous/incomplete edge cases
└── cli.py                   # CLI entrypoint
```

---

## Supported Input Formats

| Format | Extensions | Library |
|--------|-----------|---------|
| NetCDF | `.nc`, `.nc4`, `.netcdf` | `netCDF4` |
| GeoTIFF / Raster | `.tif`, `.tiff`, `.img` | `rasterio` |
| Shapefile / Vector | `.shp`, `.geojson`, `.gpkg` | `geopandas` |
| GRIB / GRIB2 | `.grib`, `.grib2`, `.grb`, `.grb2` | `cfgrib`, `xarray` |
| HDF5 | `.h5`, `.hdf5`, `.he5` | `h5py` |
| CSV / TSV | `.csv`, `.tsv` | `pandas` |

---

## Normalized Metadata Schema

Every extractor must return this exact dict shape:

```python
{
    "format":        str,            # "NetCDF", "GeoTIFF", etc.
    "title":         str | None,
    "description":   str | None,
    "institution":   str | None,
    "creator":       str | None,
    "creator_email": str | None,
    "license":       str | None,
    "references":    str | None,
    "history":       str | None,
    "conventions":   list[str],      # ["CF-1.6", "ACDD-1.3"]
    "bbox_wkt":      str | None,     # WKT POLYGON string
    "time_start":    str | None,     # ISO 8601 UTC
    "time_end":      str | None,     # ISO 8601 UTC
    "crs":           str | None,     # "EPSG:4326" or WKT
    "variables":     list[VariableInfo],
    "extra":         dict,           # format-specific metadata
}
```

### VariableInfo schema

```python
{
    "name":          str,            # raw variable name in file
    "standard_name": str | None,     # CF standard name if present
    "long_name":     str | None,     # human-readable name
    "units":         str | None,     # "K", "m s-1", etc.
    "cf_resolved":   str | None,     # resolved CF standard name
    "ontology_uri":  str | None,     # "sweet:AirTemperature"
    "theme":         str | None,     # "theme:AtmosphericConditions"
    "shape":         list[int],      # e.g. [8760, 721, 1440]
    "dimensions":    list[str],      # e.g. ["time", "lat", "lon"]
}
```

---

## CF Mappings (mappings/)

### cf_standard_names.py

Must cover at minimum these domains. Dictionary format: `"cf_standard_name": "ontology:ClassName"`

**Atmosphere — Temperature:**
- `air_temperature` → `sweet:AirTemperature`
- `surface_temperature` → `sweet:SurfaceTemperature`
- `dew_point_temperature` → `sweet:DewPointTemperature`
- `sea_surface_temperature` → `sweet:SeaSurfaceTemperature`

**Atmosphere — Precipitation & Humidity:**
- `precipitation_flux` → `sweet:Precipitation`
- `precipitation_amount` → `sweet:Precipitation`
- `lwe_precipitation_rate` → `sweet:Precipitation`
- `relative_humidity` → `sweet:RelativeHumidity`
- `specific_humidity` → `sweet:SpecificHumidity`

**Atmosphere — Wind:**
- `eastward_wind` → `sweet:WindVelocity`
- `northward_wind` → `sweet:WindVelocity`
- `wind_speed` → `sweet:WindSpeed`
- `wind_speed_of_gust` → `sweet:WindGust`
- `wind_from_direction` → `sweet:WindDirection`

**Atmosphere — Pressure & Radiation:**
- `air_pressure` → `sweet:AtmosphericPressure`
- `air_pressure_at_mean_sea_level` → `sweet:AtmosphericPressure`
- `surface_downwelling_shortwave_flux_in_air` → `sweet:SolarRadiation`
- `surface_upward_latent_heat_flux` → `sweet:LatentHeat`
- `surface_upward_sensible_heat_flux` → `sweet:SensibleHeat`

**Hydrology:**
- `runoff_flux` → `sweet:Runoff`
- `soil_moisture_content` → `sweet:SoilMoisture`
- `volumetric_soil_water_layer` → `sweet:SoilMoisture`
- `water_evaporation_flux` → `sweet:Evaporation`

**Ocean:**
- `sea_water_temperature` → `sweet:SeaWaterTemperature`
- `sea_water_salinity` → `sweet:Salinity`
- `sea_surface_height_above_geoid` → `sweet:SeaSurfaceHeight`
- `sea_ice_area_fraction` → `sweet:SeaIce`

**Cryosphere:**
- `land_ice_thickness` → `sweet:IceThickness`
- `snow_depth` → `sweet:SnowDepth`
- `surface_snow_amount` → `sweet:SnowCover`

**Land:**
- `leaf_area_index` → `envo:LeafAreaIndex`
- `normalized_difference_vegetation_index` → `envo:NDVI`
- `land_cover` → `envo:LandCover`
- `soil_type` → `envo:SoilType`
- `surface_altitude` → `sweet:Elevation`

### cf_short_aliases.py

Short variable name → CF standard name. Must include ERA5, CMIP6, CORDEX common aliases:

```python
CF_SHORT_ALIASES = {
    "t2m": "air_temperature",
    "tas": "air_temperature",
    "tp":  "precipitation_flux",
    "pr":  "precipitation_flux",
    "u10": "eastward_wind",
    "v10": "northward_wind",
    "uas": "eastward_wind",
    "vas": "northward_wind",
    "sp":  "air_pressure",
    "msl": "air_pressure_at_mean_sea_level",
    "sst": "sea_surface_temperature",
    "tos": "sea_surface_temperature",
    "d2m": "dew_point_temperature",
    "hurs":"relative_humidity",
    "huss":"specific_humidity",
    "sfcWind": "wind_speed",
    "si10": "wind_speed",
    "rsds": "surface_downwelling_shortwave_flux_in_air",
    "snd":  "snow_depth",
    "snw":  "surface_snow_amount",
    "mrso": "soil_moisture_content",
    "lai":  "leaf_area_index",
    "ndvi": "normalized_difference_vegetation_index",
    "ro":   "runoff_flux",
    "e":    "water_evaporation_flux",
    "siconc": "sea_ice_area_fraction",
    "skt":  "surface_temperature",
    "stl1": "soil_temperature",
    "swvl1":"volumetric_soil_water_layer",
    "sd":   "snow_depth",
    "10u":  "eastward_wind",
    "10v":  "northward_wind",
    "2t":   "air_temperature",
}
```

### themes.py

Ontology URI → INSPIRE dcat:theme:

```python
THEME_MAPPING = {
    "sweet:AirTemperature":       "theme:AtmosphericConditions",
    "sweet:Precipitation":        "theme:HydrologicalConditions",
    "sweet:WindSpeed":            "theme:AtmosphericConditions",
    "sweet:WindVelocity":         "theme:AtmosphericConditions",
    "sweet:AtmosphericPressure":  "theme:AtmosphericConditions",
    "sweet:SolarRadiation":       "theme:AtmosphericConditions",
    "sweet:SeaSurfaceTemperature":"theme:OceanConditions",
    "sweet:Salinity":             "theme:OceanConditions",
    "sweet:SeaSurfaceHeight":     "theme:OceanConditions",
    "sweet:SeaIce":               "theme:CryosphericConditions",
    "sweet:Runoff":               "theme:HydrologicalConditions",
    "sweet:SoilMoisture":         "theme:LandSurfaceConditions",
    "sweet:SnowDepth":            "theme:CryosphericConditions",
    "sweet:IceThickness":         "theme:CryosphericConditions",
    "sweet:Elevation":            "theme:ElevationConditions",
    "envo:NDVI":                  "theme:LandSurfaceConditions",
    "envo:LeafAreaIndex":         "theme:LandSurfaceConditions",
    "envo:LandCover":             "theme:LandSurfaceConditions",
}
```

---

## DCAT 3 JSON-LD Output Schema

### Required fields (always present)

```json
{
  "@context": { ... },
  "@type": "dcat:Dataset",
  "@id": "urn:dataset:{slug}",
  "dct:title": { "@value": "...", "@language": "en" },
  "dct:format": "NetCDF",
  "dct:modified": "2024-01-01T00:00:00Z",
  "dcat:theme": [{ "@id": "theme:AtmosphericConditions" }],
  "cf:ontologyMappings": [{ "@id": "sweet:AirTemperature" }],
  "cf:variableMappings": [
    {
      "cf:variableName": "t2m",
      "cf:standardName": "air_temperature",
      "cf:longName": "2 metre temperature",
      "cf:units": "K",
      "cf:ontologyURI": "sweet:AirTemperature",
      "cf:dimensions": ["time", "latitude", "longitude"],
      "cf:shape": [8760, 721, 1440]
    }
  ]
}
```

### Optional fields (include when available)

```json
{
  "dct:description": { "@value": "...", "@language": "en" },
  "dct:publisher": { "@type": "foaf:Organization", "foaf:name": "ECMWF" },
  "dct:creator": { "@type": "foaf:Person", "foaf:name": "...", "foaf:mbox": "mailto:..." },
  "dct:spatial": {
    "@type": "dct:Location",
    "geo:asWKT": { "@type": "geo:wktLiteral", "@value": "POLYGON(...)" },
    "dct:conformsTo": "EPSG:4326"
  },
  "dct:temporal": {
    "@type": "dct:PeriodOfTime",
    "dcat:startDate": { "@type": "xsd:dateTime", "@value": "2020-01-01T00:00:00Z" },
    "dcat:endDate":   { "@type": "xsd:dateTime", "@value": "2023-12-31T23:59:59Z" }
  },
  "dct:conformsTo": [{ "@id": "cf:CF-1.6" }, { "@id": "cf:ACDD-1.3" }],
  "dct:license": { "@id": "https://creativecommons.org/licenses/by/4.0/" },
  "dct:references": "https://doi.org/...",
  "prov:wasGeneratedBy": { "@type": "prov:Activity", "prov:description": "..." },
  "dcat:extras": { }
}
```

### JSON-LD @context (always use this exact context)

```json
{
  "dcat":  "http://www.w3.org/ns/dcat#",
  "dct":   "http://purl.org/dc/terms/",
  "xsd":   "http://www.w3.org/2001/XMLSchema#",
  "foaf":  "http://xmlns.com/foaf/0.1/",
  "prov":  "http://www.w3.org/ns/prov#",
  "geo":   "http://www.opengis.net/ont/geosparql#",
  "sweet": "http://sweetontology.net/repr#",
  "envo":  "http://purl.obolibrary.org/obo/ENVO_",
  "theme": "http://inspire.ec.europa.eu/theme/",
  "cf":    "http://cfconventions.org/cf-conventions/"
}
```

---

## Public API

```python
# Single file conversion
from geo2dcat import convert
result: dict = convert("era5_temp.nc")
result: dict = convert("dem_europe.tif")
result: dict = convert("floods.shp")
result: dict = convert("forecast.grib2")
result: dict = convert("satellite.h5")
result: dict = convert("stations.csv")

# With custom dataset URI
result = convert("era5_temp.nc", dataset_id="https://myorg.eu/datasets/era5-2023")

# Save to file
from geo2dcat import convert_to_file
output_path: str = convert_to_file("era5_temp.nc", "output.dcat.jsonld")

# Batch convert directory
from geo2dcat import batch_convert
results: list[dict] = batch_convert("./data/")
# Each result: {"file": str, "status": "ok"|"error", "dcat": dict, "error": str}
```

---

## SHACL Generator (shacl_generator.py)

### Purpose

Takes a batch of DCAT outputs (from multiple files of same type/source) and generates a minimal SHACL shapes file.

### Algorithm

1. Collect all property keys across all DCAT outputs in batch
2. Calculate presence frequency per property (0.0 → 1.0)
3. Properties with frequency ≥ 0.95 → `sh:minCount 1` (mandatory)
4. Properties with frequency < 0.95 → `sh:minCount 0` (optional)
5. Infer `sh:datatype` from values (xsd:string, xsd:dateTime, geo:wktLiteral, etc.)
6. Collect unique `dcat:theme` values → `sh:in` constraint
7. Output: Turtle format SHACL shapes file

### Input

```python
from geo2dcat.shacl_generator import generate_shacl

shacl_turtle: str = generate_shacl(
    dcat_outputs=list_of_dcat_dicts,  # list of DCAT JSON-LD dicts
    shape_name="ClimateDatasetShape",
    output_path="climate.shacl.ttl",  # optional, saves to file
)
```

### Output example

```turtle
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct:  <http://purl.org/dc/terms/> .

:ClimateDatasetShape
    a sh:NodeShape ;
    sh:targetClass dcat:Dataset ;

    sh:property [
        sh:path dct:title ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
    ] ;

    sh:property [
        sh:path dct:spatial ;
        sh:minCount 1 ;
    ] ;

    sh:property [
        sh:path dcat:theme ;
        sh:minCount 0 ;
        sh:in (
            theme:AtmosphericConditions
            theme:HydrologicalConditions
            theme:OceanConditions
        ) ;
    ] .
```

---

## Synthetic Data Generator (synthetic/)

### Purpose

Generate labeled training pairs for DLLM fine-tuning. Only generates **hard cases** — ambiguous or incomplete inputs that the rule-based geo2dcat system cannot resolve correctly.

### Training pair format (JSONL output)

```jsonl
{"input": {...normalized_metadata...}, "output": {...dcat_jsonld...}, "difficulty": "hard", "scenario": "ambiguous_variable"}
{"input": {...}, "output": {...}, "difficulty": "hard", "scenario": "missing_standard_name"}
```

### Hard case scenarios to generate

1. **ambiguous_variable_names** — variable named `temp`, `flux`, `anomaly`, `level`, `index` with no standard_name
2. **missing_standard_name** — has long_name and units but no standard_name; must infer from context
3. **conflicting_metadata** — title says "precipitation" but variables look like temperature
4. **non_cf_conventions** — file uses custom variable names not in CF table
5. **partial_spatial** — only lat range given, no lon; or only single point
6. **description_only** — no structured metadata; only free-text description to parse

### SyntheticGenerator class

```python
from geo2dcat.synthetic import SyntheticGenerator

gen = SyntheticGenerator(
    seed_dcat_dir="./dcat_outputs/",    # real DCAT outputs to augment
    anthropic_api_key=None,             # optional, for Claude-generated hard cases
)

dataset = gen.generate(
    augment_count=2000,     # variations of real pairs
    template_count=3000,    # template-based hard cases
    claude_count=1000,      # Claude API hard cases (requires api_key)
    output_path="training_data.jsonl",
    seed=42,
)

# Returns summary
# {"total": 6000, "augmented": 2000, "template": 3000, "claude": 1000, "path": "..."}
```

### Claude API prompt (for hard cases)

When `claude_count > 0`, use the Anthropic API with this system prompt:

```
You are a geospatial metadata expert specializing in DCAT 3 and CF Conventions.

Given ambiguous or incomplete technical metadata from a scientific dataset file,
produce the correct DCAT 3 JSON-LD output with proper ontology mappings.

Rules:
- Use SWEET ontology URIs for atmospheric/ocean/cryo variables
- Use ENVO ontology URIs for land/ecological variables  
- Use INSPIRE themes for dcat:theme
- If standard_name cannot be determined, set cf:ontologyURI to null
- Confidence score (0.0-1.0) must be included per variable mapping
- Return ONLY valid JSON, no explanation

Output format: DCAT 3 JSON-LD as specified in the context.
```

---

## CLI

### Installation

```bash
pip install geo2dcat              # core only (NetCDF)
pip install geo2dcat[geotiff]     # + GeoTIFF
pip install geo2dcat[shapefile]   # + Shapefile
pip install geo2dcat[grib]        # + GRIB
pip install geo2dcat[hdf5]        # + HDF5
pip install geo2dcat[csv]         # + CSV
pip install geo2dcat[all]         # all formats
```

### Commands

```bash
# Convert single file → stdout
geo2dcat convert era5_temp.nc

# Convert single file → output file
geo2dcat convert era5_temp.nc --output catalog.jsonld

# Convert with custom dataset URI
geo2dcat convert era5_temp.nc --id "https://myorg.eu/datasets/era5-2023"

# Show only variable mappings
geo2dcat convert era5_temp.nc --variables-only

# Batch convert directory
geo2dcat batch ./data/ --output full_catalog.jsonld

# Batch convert with pattern filter
geo2dcat batch ./data/ --pattern "**/*.nc" --output netcdf_catalog.jsonld

# Generate SHACL from directory
geo2dcat shacl ./data/ --shape-name ClimateDatasetShape --output climate.shacl.ttl

# Generate synthetic training data
geo2dcat synthetic \
  --seed-dir ./dcat_outputs/ \
  --augment 2000 \
  --templates 3000 \
  --claude 1000 \
  --output training_data.jsonl \
  --api-key $ANTHROPIC_API_KEY

# Show supported formats
geo2dcat formats

# Show CF mappings for a variable
geo2dcat lookup t2m
geo2dcat lookup air_temperature
```

### CLI output format

- Default: pretty-printed JSON to stdout
- `--output file.jsonld`: save to file, print summary to stdout
- `--quiet`: suppress all output except errors
- `--format turtle`: output as RDF Turtle instead of JSON-LD (requires rdflib)

---

## pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "geo2dcat"
version = "0.1.0"
description = "Convert geospatial & scientific file formats to DCAT 3 JSON-LD with CF ontology mappings"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.9"
keywords = ["netcdf", "dcat", "cf-conventions", "climate", "geospatial", "rdf", "json-ld", "knowledge-graph"]
dependencies = ["numpy>=1.24.0"]

[project.optional-dependencies]
netcdf    = ["netCDF4>=1.6.0"]
geotiff   = ["rasterio>=1.3.0"]
shapefile = ["geopandas>=0.13.0", "fiona>=1.9.0"]
grib      = ["cfgrib>=0.9.10", "xarray>=2023.1.0", "pandas>=2.0.0"]
hdf5      = ["h5py>=3.8.0"]
csv       = ["pandas>=2.0.0"]
synthetic = ["anthropic>=0.25.0"]
rdf       = ["rdflib>=6.3.0"]
all = [
    "netCDF4>=1.6.0", "rasterio>=1.3.0", "geopandas>=0.13.0",
    "fiona>=1.9.0", "cfgrib>=0.9.10", "xarray>=2023.1.0",
    "h5py>=3.8.0", "pandas>=2.0.0", "anthropic>=0.25.0",
    "rdflib>=6.3.0",
]
dev = ["pytest>=7.0", "pytest-cov", "ruff", "mypy"]

[project.scripts]
geo2dcat = "geo2dcat.cli:main"

[project.urls]
Homepage = "https://github.com/yourusername/geo2dcat"
```

---

## Error Handling

- Unsupported format → `ValueError: Unsupported format: .xyz`
- File not found → `FileNotFoundError`
- Missing optional dependency → `ImportError` with install instruction
- Extraction failure → return partial result with `"error"` key, never crash
- Batch processing → per-file errors collected, processing continues

---

## Testing Requirements

```
tests/
├── test_netcdf.py       # test with sample .nc file
├── test_geotiff.py      # test with sample .tif file
├── test_shapefile.py    # test with sample .shp file
├── test_grib.py         # test with sample .grib file
├── test_hdf5.py         # test with sample .h5 file
├── test_csv.py          # test with sample .csv file
├── test_dcat_builder.py # test JSON-LD output structure
├── test_shacl.py        # test SHACL generation
├── test_cli.py          # test CLI commands
└── fixtures/            # small sample files for each format
```

Each test must verify:
1. Output is valid JSON
2. `@type` is `dcat:Dataset`
3. `@context` contains all required prefixes
4. `cf:variableMappings` is a list
5. `dct:spatial` uses valid WKT if bbox present
6. `dct:temporal` uses valid ISO 8601 if time present

---

## Notes for Implementation

- All extractors must handle **header-only reading** — never load full file data into memory, only metadata
- Variable coordinate names (`lat`, `lon`, `time`, `level`) must be excluded from `cf:variableMappings`
- If `standard_name` is missing but `long_name` is present, attempt alias lookup before giving up
- SHACL generator clusters by `dct:format` — ERA5 NetCDF and CMIP6 NetCDF may get different shapes
- Synthetic generator hard cases must have `"difficulty": "hard"` in output JSONL
- Claude API calls in synthetic generator must be async with rate limiting (max 10 concurrent)
