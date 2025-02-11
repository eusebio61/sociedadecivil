import requests
from sociedadecivil.base import config, tracing

tracer = tracing.get_tracer(__name__)

def convert_date(date):
    import time
    return time.strftime('%Y-%m-%d', time.strptime(date, '%d-%m-%Y'))

with tracer.start_span("contract-list") as root_span:

    with tracer.start_span("fetch") as span:

        span.add_event("Requesting contracts list", {"verbosity_level": "debug"})

        search_response = requests.post(
            'https://www.base.gov.pt/Base4/pt/resultados/',
            data={
                "type": "search_contratos",
                "version": 134.0,
                "sort": "-publicationDate",
                "page": 0,
                "size": 25
            },
            headers={
                'User-Agent': f'Mozilla/5.0 ({config.platform_name})'
            }
        )
        
        span.add_event("Request fulfilled", {"verbosity_level": "debug"})

        if search_response.ok:
            try:
                search_results = search_response.json()
            except Exception as ex:
                tracing.error("Got a response but the expected Json is unparsable", ex)
                raise ex
        else:
            ex = Exception(f'HTTP Error: {search_response.status_code}')
            tracing.error(f"Unable to retrieve a valid response from server: {search_response.status_code}", ex)
            raise ex

    with tracer.start_span("persist") as span:

        import duckdb
        db = duckdb.connect('contracts_raw.db')

        fields = {
            "id": {
                "name": "id",
                "db_type": "INTEGER NOT NULL PRIMARY KEY"
            },
            "type": {
                "name": "contractingProcedureType",
                "db_type": "VARCHAR"
            },
            "publication_date": {
                "name": "publicationDate",
                "db_type": "DATE",
                'proc': lambda v: convert_date(v)
            },
            "contracted": {
                "name": "contracted",
                "db_type": "VARCHAR"
            },
            "contracting": {
                "name": "contracting",
                "db_type": "VARCHAR"
            },
            "description": {
                "name": "objectBriefDescription",
                "db_type": "VARCHAR"
            },
            "initial_price": {
                "name": "initialContractualPrice",
                "db_type": "VARCHAR"
            },
            "signing_date": {
                "name": "signingDate",
                "db_type": "DATE",
                'proc': lambda v: convert_date(v)
            },
        }

        table_fields = ", ".join([f'{field} {fields[field]["db_type"]}' for field in fields])

        db.sql(f'CREATE TABLE IF NOT EXISTS contracts ({table_fields})')

        for result in search_results['items']:
            values = [
                result[fields[field]['name']]
                if 'proc' not in fields[field]
                else fields[field]['proc'](result[fields[field]['name']])
                for field in fields
            ]
            db.execute('INSERT INTO contracts VALUES (?, ?, ?, ?, ?, ?, ?, ?)', values)


