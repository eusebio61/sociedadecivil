import requests
import duckdb

from sociedadecivil.base import config, tracing

tracer = tracing.get_tracer(__name__)

def get_dataset_list(page, page_size):

    with tracer.start_span("dataset-list") as span:

        span.debug("Requesting datasets page")

        response = requests.get(
            'https://dados.gov.pt/api/2/datasets/search/',
            params = {
                'page': page,
                'page_size': page_size
            }
        )

        result = response.json()
        datasets = result['data']

        span.debug(f"Retrieved a list of {len(datasets)} datasets")
        
        for dataset in datasets:
            
            span.debug(f"Retrieving resources list for dataset {dataset['title']}")
            
            resources_response = requests.get(
                f'https://dados.gov.pt/api/2/datasets/{dataset["id"]}/resources',
                params = {
                    'page': 1,
                    'page_size': 50
                }
            )
            
            resources_result = resources_response.json()
            # TODO: if resources_result['next_page']
            dataset['resources'] = resources_result['data']
            
            span.debug(f"Got {len(dataset['resources'])} resources for dataset {dataset['title']}")
        
        return result

def download_resource(resource):
    pass

def persist_datasets(datasets, db_connection):
    
    db_connection.sql(
        """
        CREATE TABLE IF NOT EXISTS dados_datasets (
            id VARCHAR,
            org VARCHAR,
            title VARCHAR,
            description VARCHAR,
            resource_id VARCHAR UNIQUE,
            resource_title VARCHAR,
            resource_description VARCHAR,
            resource_format VARCHAR,
            last_modified TIMESTAMPTZ,
        )
        """
    )
    
    with tracer.start_span("resources-process") as span:

        for dataset in datasets:
            for resource in dataset['resources']:
                
                db_hits = db_connection.execute(
                    f"""
                    SELECT resource_id, last_modified
                    FROM dados_datasets
                    WHERE resource_id='{resource["id"]}'
                    """
                ).fetchall()
                
                if len(db_hits) > 0:
                    resource_id, last_modified = db_hits[0]
                    
                    if last_modified != resource['last_modified']:
                        download_resource(resource)
                    else:
                        span.debug(f'Resource {resource_id} already exists')
                else:
                    
                    values = [
                        dataset['id'],
                        dataset['organization']['name'],
                        dataset['title'],
                        dataset['description'],
                        resource['id'],
                        resource['title'],
                        resource['description'],
                        resource['format'],
                        resource['last_modified']
                    ]
                    
                    db_connection.execute(
                        'INSERT INTO dados_datasets VALUES (?,?,?,?,?,?,?,?,?)',
                        values
                    )
                    
                    download_resource(resource) # TODO: The path to which the resource is downloaded should be persisted in the db too.

import duckdb
db = duckdb.connect('contracts_raw.db')


result = {
    'next_page': 1
}

while result['next_page'] is not None:
    result = get_dataset_list(1, 10)
    datasets = result['data']
    persist_datasets(datasets, db)
    

for dataset in datasets:
    for resource in dataset['resources']:
        print(f'{dataset["title"]}:{resource["title"]}:{resource["description"]}:{resource["format"]}')




