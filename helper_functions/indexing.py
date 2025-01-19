from elasticsearch import Elasticsearch
from tqdm.auto import tqdm


def index_documents(
    documents: list[dict],
    es_client: Elasticsearch,
    index_name: str = "sec-filing-index",
    dims: int = 768,
    similarity: str = "cosine",
) -> None:
    """
    Indexes the documents in Elasticsearch.

    Args:
        documents (list[dict]): Documents to index.
        es_client (Elasticsearch): Elasticsearch client.
        index_name (str, optional): Index name. Defaults to "sec-filing-index".
        dims (int, optional): Dense vector length. Defaults to 768.
        similarity (str, optional): Similarity metric to use. Defaults to "cosine".
    """

    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)

    index_settings = {
        "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "company": {"type": "keyword"},
                "reporting_period": {"type": "text"},
                "filing_type": {"type": "text"},
                "text": {"type": "text"},
                "section": {"type": "text"},
                "id": {"type": "keyword"},
                "text_vector": {
                    "type": "dense_vector",
                    "dims": dims,
                    "index": True,
                    "similarity": similarity,
                },
                "non_text_vector": {
                    "type": "dense_vector",
                    "dims": dims,
                    "index": True,
                    "similarity": similarity,
                },
                "all_vector": {
                    "type": "dense_vector",
                    "dims": dims,
                    "index": True,
                    "similarity": similarity,
                },
            }
        },
    }

    es_client.indices.create(index=index_name, body=index_settings)

    for doc in tqdm(documents):
        try:
            es_client.index(index=index_name, document=doc)
        except Exception as e:
            print(e)
