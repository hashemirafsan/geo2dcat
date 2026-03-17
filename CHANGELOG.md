# Changelog

All notable changes to geo2dcat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Roadmap section in README with planned features
- Support for Zarr format (planned)
- STAC output format (planned)
- Web service API (planned)

## [0.1.0] - 2026-03-18

### Added
- Initial release of geo2dcat
- Multi-format support for NetCDF, GeoTIFF, Shapefile, GRIB, HDF5, and CSV
- DCAT 3 JSON-LD output with CF Convention extensions
- Comprehensive CF standard name to ontology mappings (100+ variables)
- SWEET and ENVO ontology URI mappings
- INSPIRE theme categorization
- CLI interface with convert, batch, shacl, lookup, and synthetic commands
- Python API with convert(), convert_to_file(), and batch_convert() functions
- Docker environment with GDAL/PROJ/GEOS pre-configured
- SHACL shape generation from dataset collections
- Synthetic data generator for DLLM training
- Comprehensive test suite with fixtures
- Full documentation and examples
- Integration with Apache Jena Fuseki for SPARQL queries
- Memory-efficient metadata extraction (no data loading)
- Support for ERA5, CMIP6, and CORDEX variable aliases
- Extensible plugin architecture for new formats

### Security
- Safe file path handling with pathlib
- Input validation for all file operations
- Sandboxed Docker environment

[Unreleased]: https://github.com/hashemirafsan/geo2dcat/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hashemirafsan/geo2dcat/releases/tag/v0.1.0