#!/usr/bin/env python3
"""
Basic usage examples for geo2dcat library.

This script demonstrates common use cases for converting geospatial
datasets to DCAT 3 JSON-LD format.
"""

import json
from pathlib import Path
from geo2dcat import convert, convert_to_file, batch_convert


def example_single_file_conversion():
    """Convert a single NetCDF file to DCAT JSON-LD."""
    print("=== Single File Conversion ===")
    
    # Convert a NetCDF file
    metadata = convert("../data/HWD_EU_health_rcp45_stdev_v1.0.nc")
    
    # Pretty print the result
    print(json.dumps(metadata, indent=2))
    
    # Access specific fields
    print(f"\nTitle: {metadata['dct:title']['@value']}")
    print(f"Format: {metadata['dct:format']}")
    print(f"Number of variables: {len(metadata['cf:variableMappings'])}")
    
    return metadata


def example_save_to_file():
    """Convert and save to a file."""
    print("\n=== Save to File ===")
    
    # Convert and save in one step
    output_path = convert_to_file(
        "../data/HWD_EU_health_rcp45_stdev_v1.0.nc",
        "../outputs/example_output.jsonld"
    )
    
    print(f"Saved to: {output_path}")
    
    # Read and verify
    with open(output_path) as f:
        saved_metadata = json.load(f)
    
    print(f"Verified: {saved_metadata['@type']} with ID {saved_metadata['@id']}")


def example_custom_dataset_id():
    """Convert with a custom dataset URI."""
    print("\n=== Custom Dataset ID ===")
    
    metadata = convert(
        "../data/HWD_EU_health_rcp45_stdev_v1.0.nc",
        dataset_id="https://climate-data.eu/datasets/hwd-health-2024"
    )
    
    print(f"Custom ID: {metadata['@id']}")


def example_batch_conversion():
    """Batch convert multiple files."""
    print("\n=== Batch Conversion ===")
    
    # Convert all NetCDF files
    results = batch_convert("../data/", pattern="**/*.nc")
    
    # Summary
    successful = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] == "error"]
    
    print(f"Processed {len(results)} files:")
    print(f"  - Successful: {len(successful)}")
    print(f"  - Failed: {len(failed)}")
    
    # Show details
    for result in results[:3]:  # First 3 files
        if result["status"] == "ok":
            title = result["dcat"]["dct:title"]["@value"]
            print(f"  ✓ {Path(result['file']).name} → {title}")
        else:
            print(f"  ✗ {Path(result['file']).name} → {result['error']}")
    
    return results


def example_create_catalog():
    """Create a DCAT catalog from multiple datasets."""
    print("\n=== Create DCAT Catalog ===")
    
    # Batch convert
    results = batch_convert("../data/", pattern="**/*.nc")
    
    # Extract successful conversions
    datasets = [r["dcat"] for r in results if r["status"] == "ok"]
    
    # Create catalog
    catalog = {
        "@context": {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dct": "http://purl.org/dc/terms/",
            "foaf": "http://xmlns.com/foaf/0.1/"
        },
        "@type": "dcat:Catalog",
        "@id": "https://climate-data.eu/catalog/2024",
        "dct:title": {
            "@value": "Climate Data Catalog 2024",
            "@language": "en"
        },
        "dct:description": {
            "@value": "Collection of climate datasets with DCAT metadata",
            "@language": "en"
        },
        "dct:publisher": {
            "@type": "foaf:Organization",
            "foaf:name": "Climate Data Initiative"
        },
        "dcat:dataset": datasets
    }
    
    # Save catalog
    catalog_path = Path("../outputs/catalog.jsonld")
    catalog_path.write_text(json.dumps(catalog, indent=2))
    
    print(f"Created catalog with {len(datasets)} datasets")
    print(f"Saved to: {catalog_path}")
    
    return catalog


def example_inspect_variables():
    """Inspect variable mappings in detail."""
    print("\n=== Variable Inspection ===")
    
    metadata = convert("../data/HWD_EU_health_rcp45_stdev_v1.0.nc")
    
    print("Variables found:")
    for var in metadata["cf:variableMappings"]:
        print(f"\n  Variable: {var['cf:variableName']}")
        print(f"    Standard name: {var.get('cf:standardName', 'N/A')}")
        print(f"    Long name: {var.get('cf:longName', 'N/A')}")
        print(f"    Units: {var.get('cf:units', 'N/A')}")
        print(f"    Ontology: {var.get('cf:ontologyURI', 'N/A')}")
        print(f"    Shape: {var.get('cf:shape', [])}")
        print(f"    Dimensions: {var.get('cf:dimensions', [])}")


def example_filter_by_theme():
    """Filter datasets by INSPIRE theme."""
    print("\n=== Filter by Theme ===")
    
    results = batch_convert("../data/", pattern="**/*.nc")
    
    # Group by theme
    by_theme = {}
    for result in results:
        if result["status"] == "ok":
            themes = result["dcat"].get("dcat:theme", [])
            for theme in themes:
                theme_id = theme["@id"]
                if theme_id not in by_theme:
                    by_theme[theme_id] = []
                by_theme[theme_id].append(result["file"])
    
    print("Datasets by theme:")
    for theme, files in by_theme.items():
        print(f"\n  {theme}:")
        for f in files[:3]:  # First 3 files
            print(f"    - {Path(f).name}")


def main():
    """Run all examples."""
    print("geo2dcat Usage Examples")
    print("=" * 50)
    
    # Check if data directory exists
    data_dir = Path("../data")
    if not data_dir.exists() or not any(data_dir.glob("*.nc")):
        print("Error: No data files found in ../data/")
        print("Please add some NetCDF, GeoTIFF, or other supported files first.")
        return
    
    # Run examples
    try:
        example_single_file_conversion()
        example_save_to_file()
        example_custom_dataset_id()
        example_batch_conversion()
        example_create_catalog()
        example_inspect_variables()
        example_filter_by_theme()
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have installed geo2dcat and have data files available.")


if __name__ == "__main__":
    main()