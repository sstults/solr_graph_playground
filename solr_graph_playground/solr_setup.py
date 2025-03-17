import json
import requests
import click
from typing import List, Dict, Any
import sys
import random

@click.group()
def cli():
    """Commands for managing Solr citation graph collection"""
    pass

def collection_exists():
    """Internal function to check if collection exists"""
    r = requests.get('http://localhost:8983/solr/admin/collections',
                    params={'action': 'LIST'})
    collections = r.json()['collections']
    return 'citation_graph' in collections

@cli.command()
def check_collection():
    """Check if citation_graph collection exists"""
    if collection_exists():
        print("citation_graph collection exists")
        return True
    else:
        print("citation_graph collection does not exist")
        return False

@cli.command()
def create_collection():
    """Create citation_graph collection and configure schema"""
    if collection_exists():
        print("citation_graph collection already exists")
        return
        
    print("Creating citation_graph collection...")
    # Create collection with 2 shards
    r = requests.get('http://localhost:8983/solr/admin/collections', 
                    params={
                        'action': 'CREATE',
                        'name': 'citation_graph',
                        'numShards': 2,
                        'replicationFactor': 1,
                        'collection.configName': '_default',
                        'maxShardsPerNode': 2
                    })
    
    if r.status_code != 200:
        raise Exception(f"Failed to create collection: {r.text}")
        
    # Configure schema
    schema_fields = [
        {
            "name": "id",
            "type": "plong",
            "stored": True
        },
        {
            "name": "title",
            "type": "text_general",
            "stored": True
        },
        {
            "name": "year",
            "type": "pint",
            "stored": True
        },
        {
            "name": "publisher",
            "type": "text_general",
            "stored": True
        },
        {
            "name": "doi",
            "type": "string",
            "stored": True
        },
        {
            "name": "author_names",
            "type": "text_general",
            "stored": True,
            "multiValued": True
        },
        {
            "name": "references",
            "type": "plongs",
            "stored": True,
            "multiValued": True
        }
    ]
    
    # Add fields to schema
    for field in schema_fields:
        # Check if field exists
        r = requests.get('http://localhost:8983/solr/citation_graph/schema/fields')
        existing_fields = {f['name'] for f in r.json()['fields']}
        
        if field['name'] not in existing_fields:
            r = requests.post(
                'http://localhost:8983/solr/citation_graph/schema',
                json={"add-field": field}
            )
            if r.status_code != 200:
                raise Exception(f"Failed to add field {field['name']}: {r.text}")
    
    print("Collection created and schema configured successfully")

@cli.command()
def delete_collection():
    """Delete the citation_graph collection if it exists"""
    if not collection_exists():
        print("citation_graph collection does not exist")
        return
        
    print("Deleting citation_graph collection...")
    r = requests.get('http://localhost:8983/solr/admin/collections',
                    params={
                        'action': 'DELETE',
                        'name': 'citation_graph'
                    })
    
    if r.status_code != 200:
        raise Exception(f"Failed to delete collection: {r.text}")
    
    print("Collection deleted successfully")

@cli.command()
@click.argument('num_samples', type=int)
def get_random_sample(num_samples):
    """Get random documents from the collection using Solr's random sort

    Arguments:
        num_samples: Number of random samples to retrieve
    """
    if not collection_exists():
        print("citation_graph collection does not exist")
        return

    # Generate random seed
    seed = random.randint(0, 1000000)
    
    # Use Solr's random sort functionality
    r = requests.get('http://localhost:8983/solr/citation_graph/select',
                    params={
                        'q': '*:*',
                        'rows': str(num_samples),
                        'sort': f'random_{seed} desc'
                    })
    
    if r.status_code != 200:
        raise Exception(f"Failed to get random sample: {r.text}")
    
    docs = r.json()['response']['docs']
    print(json.dumps(docs, indent=2))

@cli.command()
def recreate_collection():
    """Delete the collection if it exists and create it fresh"""
    if collection_exists():
        print("Deleting existing citation_graph collection...")
        r = requests.get('http://localhost:8983/solr/admin/collections',
                        params={
                            'action': 'DELETE',
                            'name': 'citation_graph'
                        })
        
        if r.status_code != 200:
            raise Exception(f"Failed to delete collection: {r.text}")
        
        print("Collection deleted successfully")
    
    # Then create fresh
    create_collection()

def transform_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a DBLP record to match Solr schema"""
    # Extract author names from author objects
    author_names = [author['name'] for author in record.get('authors', [])]
    
    # Create new record with Solr schema
    return {
        'id': record['id'],
        'title': record.get('title', ''),
        'year': record.get('year', None),
        'publisher': record.get('publisher', ''),
        'doi': record.get('doi', ''),
        'author_names': author_names,
        'references': record.get('references', [])
    }

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--batch-size', default=1000, help='Number of records to send in each batch')
def ingest_citations(input_file: str, batch_size: int):
    """Ingest citations from a JSON Lines file into the citation_graph collection"""
    if not collection_exists():
        print("citation_graph collection does not exist. Creating...")
        create_collection()
    
    batch: List[Dict[str, Any]] = []
    total_records = 0
    
    print(f"Ingesting records from {input_file} in batches of {batch_size}...")
    
    try:
        with open(input_file) as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    transformed = transform_record(record)
                    batch.append(transformed)
                    
                    if len(batch) >= batch_size:
                        r = requests.post(
                            'http://localhost:8983/solr/citation_graph/update/json/docs',
                            json=batch,
                            params={'commit': 'true'}
                        )
                        if r.status_code != 200:
                            print(f"Error ingesting batch: {r.text}", file=sys.stderr)
                            continue
                            
                        total_records += len(batch)
                        print(f"Ingested {total_records} records...", end='\r')
                        batch = []
                        
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON line: {e}", file=sys.stderr)
                    continue
                except Exception as e:
                    print(f"Error processing record: {e}", file=sys.stderr)
                    continue
                    
        # Ingest any remaining records
        if batch:
            r = requests.post(
                'http://localhost:8983/solr/citation_graph/update/json/docs',
                json=batch,
                params={'commit': 'true'}
            )
            if r.status_code == 200:
                total_records += len(batch)
            
        print(f"\nCompleted ingestion of {total_records} records")
        
    except Exception as e:
        print(f"Fatal error during ingestion: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    cli.main(standalone_mode=False)
