# geo2dcat Examples

This directory contains example scripts demonstrating how to use the geo2dcat library.

## Available Examples

### basic_usage.py
Demonstrates core functionality:
- Converting single files
- Saving to disk
- Batch processing directories
- Creating DCAT catalogs
- Inspecting variable mappings
- Filtering by themes

Run with:
```bash
cd examples
python basic_usage.py
```

### sparql_integration.py
Advanced example showing:
- Converting DCAT JSON-LD to RDF
- Loading into Apache Jena Fuseki
- SPARQL queries against the knowledge graph
- Federated queries concept

Run with:
```bash
# Start Fuseki first
docker compose --profile sparql up -d

# Then run the example
python sparql_integration.py
```

## Prerequisites

Before running examples:

1. Install geo2dcat:
   ```bash
   pip install -e ".[all]"
   ```

2. Add some data files to the `data/` directory

3. For SPARQL examples, install RDF support:
   ```bash
   pip install geo2dcat[rdf]
   ```

## Adding Your Own Examples

Feel free to add examples demonstrating:
- Integration with specific tools (CKAN, GeoNode, etc.)
- Custom mappings and extensions
- Performance optimization techniques
- Real-world use cases

Name your example descriptively and add documentation!