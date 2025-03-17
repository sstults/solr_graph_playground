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
