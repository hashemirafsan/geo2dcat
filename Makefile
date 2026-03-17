build:
	docker compose build geo2dcat

shell:
	docker compose run --rm geo2dcat bash

test:
	docker compose --profile test run --rm test

generate-fixtures:
	docker compose run --rm geo2dcat python tests/fixtures/generate.py

sparql:
	docker compose --profile sparql up -d fuseki

sparql-stop:
	docker compose --profile sparql stop fuseki

jupyter:
	docker compose run --rm -p 8888:8888 geo2dcat python -m jupyter lab --ip=0.0.0.0 --no-browser --allow-root

convert:
	docker compose run --rm geo2dcat geo2dcat convert /data/$(FILE)

batch:
	docker compose run --rm geo2dcat geo2dcat batch /data/ --output /outputs/catalog.jsonld

shacl:
	docker compose run --rm geo2dcat geo2dcat shacl /data/ --output /outputs/shapes.shacl.ttl

clean:
	docker compose down --rmi local --volumes --remove-orphans
