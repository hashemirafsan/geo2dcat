#!/usr/bin/env python3
"""
Advanced example: SPARQL integration with Apache Jena Fuseki.

This example demonstrates how to:
1. Convert geospatial datasets to DCAT RDF
2. Load into a SPARQL triplestore
3. Query the knowledge graph
"""

import json
import requests
from pathlib import Path
from rdflib import Graph, Namespace, URIRef
from geo2dcat import batch_convert


# Namespaces
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")
THEME = Namespace("http://inspire.ec.europa.eu/theme/")
CF = Namespace("http://cfconventions.org/cf-conventions/")


def convert_to_rdf(json_ld_data):
    """Convert DCAT JSON-LD to RDF graph."""
    g = Graph()
    g.parse(data=json.dumps(json_ld_data), format="json-ld")
    return g


def load_to_fuseki(graph, fuseki_url="http://localhost:3030", dataset="climate-kg"):
    """Load RDF graph into Apache Jena Fuseki."""
    # Serialize to Turtle
    turtle_data = graph.serialize(format="turtle")
    
    # POST to Fuseki
    response = requests.post(
        f"{fuseki_url}/{dataset}/data",
        data=turtle_data.encode("utf-8"),
        headers={"Content-Type": "text/turtle"}
    )
    
    if response.status_code == 200:
        print(f"✓ Loaded {len(graph)} triples to Fuseki")
    else:
        print(f"✗ Failed to load: {response.status_code} - {response.text}")
    
    return response.status_code == 200


def example_queries(fuseki_url="http://localhost:3030", dataset="climate-kg"):
    """Example SPARQL queries against the knowledge graph."""
    
    sparql_endpoint = f"{fuseki_url}/{dataset}/sparql"
    
    # Query 1: Find all datasets with atmospheric conditions theme
    query1 = """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX theme: <http://inspire.ec.europa.eu/theme/>
    
    SELECT ?dataset ?title WHERE {
        ?dataset a dcat:Dataset ;
                 dct:title ?title ;
                 dcat:theme theme:AtmosphericConditions .
    }
    LIMIT 10
    """
    
    print("\n=== Datasets with Atmospheric Theme ===")
    response = requests.post(
        sparql_endpoint,
        data={"query": query1},
        headers={"Accept": "application/sparql-results+json"}
    )
    
    if response.status_code == 200:
        results = response.json()
        for binding in results["results"]["bindings"]:
            print(f"- {binding['title']['value']}")
    
    # Query 2: Find all temperature variables
    query2 = """
    PREFIX cf: <http://cfconventions.org/cf-conventions/>
    PREFIX sweet: <http://sweetontology.net/repr#>
    
    SELECT DISTINCT ?dataset ?varName ?standardName WHERE {
        ?dataset cf:variableMappings ?mapping .
        ?mapping cf:variableName ?varName ;
                 cf:standardName ?standardName ;
                 cf:ontologyURI sweet:AirTemperature .
    }
    """
    
    print("\n=== Temperature Variables ===")
    response = requests.post(
        sparql_endpoint,
        data={"query": query2},
        headers={"Accept": "application/sparql-results+json"}
    )
    
    if response.status_code == 200:
        results = response.json()
        for binding in results["results"]["bindings"]:
            print(f"- {binding['varName']['value']} ({binding['standardName']['value']})")
    
    # Query 3: Spatial coverage statistics
    query3 = """
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    
    SELECT (COUNT(DISTINCT ?dataset) as ?count) WHERE {
        ?dataset dct:spatial ?spatial .
        ?spatial geo:asWKT ?wkt .
        FILTER(CONTAINS(STR(?wkt), "POLYGON"))
    }
    """
    
    print("\n=== Spatial Coverage ===")
    response = requests.post(
        sparql_endpoint,
        data={"query": query3},
        headers={"Accept": "application/sparql-results+json"}
    )
    
    if response.status_code == 200:
        results = response.json()
        count = results["results"]["bindings"][0]["count"]["value"]
        print(f"Datasets with spatial coverage: {count}")
    
    # Query 4: Time range analysis
    query4 = """
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?dataset ?title ?startDate ?endDate WHERE {
        ?dataset a dcat:Dataset ;
                 dct:title ?title ;
                 dct:temporal ?temporal .
        ?temporal dcat:startDate ?startDate ;
                  dcat:endDate ?endDate .
    }
    ORDER BY ?startDate
    """
    
    print("\n=== Temporal Coverage ===")
    response = requests.post(
        sparql_endpoint,
        data={"query": query4},
        headers={"Accept": "application/sparql-results+json"}
    )
    
    if response.status_code == 200:
        results = response.json()
        for binding in results["results"]["bindings"][:5]:
            title = binding['title']['value']
            start = binding['startDate']['value'][:10]
            end = binding['endDate']['value'][:10]
            print(f"- {title}: {start} to {end}")


def build_climate_kg():
    """Build a climate knowledge graph from geospatial files."""
    print("=== Building Climate Knowledge Graph ===")
    
    # Convert all datasets
    results = batch_convert("../data/")
    
    # Create merged graph
    merged_graph = Graph()
    
    for result in results:
        if result["status"] == "ok":
            # Convert each dataset to RDF
            dataset_graph = convert_to_rdf(result["dcat"])
            merged_graph += dataset_graph
            print(f"✓ Added {Path(result['file']).name}")
    
    print(f"\nTotal triples: {len(merged_graph)}")
    
    # Save to file
    output_path = Path("../outputs/climate_kg.ttl")
    merged_graph.serialize(destination=str(output_path), format="turtle")
    print(f"Saved to: {output_path}")
    
    return merged_graph


def federated_query_example():
    """Example of federated SPARQL query combining multiple sources."""
    
    query = """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?dataset ?title ?org ?orgLabel WHERE {
        # Our local climate data
        ?dataset a dcat:Dataset ;
                 dct:title ?title ;
                 dct:publisher ?publisher .
        ?publisher foaf:name ?org .
        
        # Federated query to DBpedia for organization info
        SERVICE <https://dbpedia.org/sparql> {
            ?dbpediaOrg rdfs:label ?orgLabel ;
                        rdfs:comment ?orgDesc .
            FILTER(CONTAINS(LCASE(?orgLabel), LCASE(?org)))
            FILTER(LANG(?orgLabel) = "en")
        }
    }
    LIMIT 5
    """
    
    print("\n=== Federated Query Example ===")
    print("This would combine local climate data with DBpedia organization info")
    print("Query:", query[:200] + "...")


def main():
    """Run SPARQL integration examples."""
    print("geo2dcat SPARQL Integration Examples")
    print("=" * 50)
    
    # Check prerequisites
    try:
        import rdflib
    except ImportError:
        print("Error: rdflib not installed")
        print("Install with: pip install geo2dcat[rdf]")
        return
    
    # Build knowledge graph
    kg = build_climate_kg()
    
    print("\n" + "=" * 50)
    print("To load into Fuseki and run queries:")
    print("1. Start Fuseki: make sparql")
    print("2. Run: load_to_fuseki(kg)")
    print("3. Run: example_queries()")
    print("\nOr use the saved turtle file: ../outputs/climate_kg.ttl")
    
    # Show example queries
    print("\n" + "=" * 50)
    print("Example SPARQL queries you can run:")
    
    print("\n1. Find datasets by theme:")
    print("""
    SELECT ?dataset ?title WHERE {
        ?dataset a dcat:Dataset ;
                 dct:title ?title ;
                 dcat:theme <http://inspire.ec.europa.eu/theme/AtmosphericConditions> .
    }
    """)
    
    print("\n2. Find datasets with specific variables:")
    print("""
    SELECT ?dataset ?varName WHERE {
        ?dataset cf:variableMappings ?mapping .
        ?mapping cf:standardName "air_temperature" ;
                 cf:variableName ?varName .
    }
    """)
    
    # Demonstrate federated query concept
    federated_query_example()


if __name__ == "__main__":
    main()