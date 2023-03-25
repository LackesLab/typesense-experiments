import typesense
from generate_dummy_data import generate_dummy_data
from tqdm import tqdm
import numpy as np
import csv
from time import perf_counter

# Define global search request with fixed embedding to ensure fair comparison
SEARCH_REQUESTS = {
    'searches': [
        {
            'collection': 'faces',
            'q': '*',
            'vector_query': f'embedding:({np.random.randn(512).tolist()}, k:100)'
        }
    ]
}


def add_faces(client: typesense.Client, n_samples=100):
    for _ in range(n_samples):
        face_document = generate_dummy_data()
        client.collections["faces"].documents.create(face_document)


def connect_to_client(url: str = "localhost", port: int = 8108, api_key: str = "xyz"):
    client = typesense.Client({
        'api_key': api_key,
        'nodes': [{
            'host': url,
            'port': str(port),
            'protocol': 'http'
        }],
        'connection_timeout_seconds': 2
    })

    return client


def create_schema(client):
    print("Create collection")
    schema = {
        'name': 'faces',
        'fields': [
            {
                'name':  'title',
                'type':  'string'
            },
            {
                'name':  'confidence',
                'type':  'float'
            },
            {
                'name':  'coordinates',
                'type':  'int32[]'
            },
            {
                'name':  'embedding',
                'type':  'float[]',
                'num_dim':  512
            }
        ],
        'default_sorting_field': 'confidence'
    }
    try:
        tes = client.collections.create(schema)
    except typesense.exceptions.ObjectAlreadyExists:
        print("Collection already exists. Skipping...")


def search_faces(client: typesense.Client):
    common_search_params = {"exclude_fields": "embedding", "per_page" : 100}
    results = []
    try:
        res = client.multi_search.perform(
            SEARCH_REQUESTS, common_search_params)
        for doc in res["results"][0]["hits"]:
            if doc["vector_distance"] > 0.6:
                results.append(doc["document"])
    except typesense.exceptions.ObjectNotFound:
        pass
    return results


def benchmark_typesense(n_iterations=500):
    client = connect_to_client()

    client.collections['faces'].delete()

    create_schema(client)

    results = []
    # Insert first 100 documents
    for _ in tqdm(range(n_iterations)):
        t1_start = perf_counter()
        add_faces(client, 100)
        t1_stop = perf_counter()

        n_documents_in_collection = client.collections['faces'].retrieve()[
            "num_documents"]

        t2_start = perf_counter()
        n_results = len(search_faces(client))
        t2_stop = perf_counter()

        results.append([n_documents_in_collection, t1_stop -
                       t1_start, t2_stop - t2_start, n_results])

    # Write the results to a CSV file
    header = ["n_documents_in_typesense", "timing_insert",
              "timing_search", "n_search_result"]
    with open("measurements.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(results)


if __name__ == "__main__":
    benchmark_typesense()
