# Solr Graph Playground

A utility to build graph structures in Solr to experiment with the graph querying capabilities.

## Overview

This tool allows you to create and manipulate graph structures within Apache Solr, enabling experimentation with Solr's graph query features.

## Setup

1. Start Solr using Docker Compose:

```bash
docker compose up -d
```

2. Create Python virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
```

4. Install the package in development mode to enable command-line tools:

```bash
pip install -e .
```

## Command-Line Interface

The package provides several command-line tools for managing the Solr citation graph collection:

### Collection Management

```bash
# Check if the citation_graph collection exists
check-solr-collection

# Create a new citation_graph collection with proper schema
create-solr-collection

# Delete the citation_graph collection
delete-solr-collection

# Recreate the collection (delete if exists and create new)
recreate-solr-collection

# Get a random sample of 10 documents from the collection
get-random-sample
```

### Data Ingestion

```bash
# Ingest citations from a JSON file
ingest-citations PATH_TO_JSON_FILE --batch-size 1000
```

Options:
- `--batch-size`: Number of records to send in each batch (default: 1000)

## Usage

Run the citation graph example:

```bash
python examples/citation_graph.py
```

This will:

1. Create a graph of academic papers with metadata (title, authors, year, journal)
2. Establish citation relationships between papers
3. Demonstrate various graph queries like:
   - Finding papers that cite a specific paper
   - Finding papers cited by a given paper
   - Searching papers by year or other metadata

## Development

### Local Solr Instance

The project includes a Docker Compose configuration that sets up Solr with a preconfigured collection for graph data:

```bash
# Start Solr
docker-compose up -d

# Check Solr status
docker-compose ps

# View Solr logs
docker-compose logs -f solr

# Stop Solr
docker-compose down
```

Access the Solr admin interface at: http://localhost:8983/solr/
