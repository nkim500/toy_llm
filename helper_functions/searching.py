from typing import Any

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


def elastic_search_knn_query(
    embedding_model: SentenceTransformer | Any,
    query: str,
    filter_company: str,
    source: list[str],
    vector_field: str = "text_vector",
    k: int = 5,
    num_candidates: int = 10000,
) -> list[dict]:
    vector = embedding_model.encode(query).tolist()
    knn = {
        "field": vector_field,
        "query_vector": vector,
        "k": k,
        "num_candidates": num_candidates,
        "filter": {"term": {"company": filter_company}},
    }

    search_query = {
        "knn": knn,
        "_source": source,
    }

    return search_query


def elastic_search_combined_query(
    embedding_model: SentenceTransformer | Any,
    query: str,
    filter_company: str,
    source: list[str],
    vector_fields: list[str] = None,
    k: int = 5,
) -> list[dict]:
    vector = embedding_model.encode(query).tolist()

    if vector_fields is None:
        vector_fields = ["text_vector", "non_text_vector"]

    script_sources = ""
    for i in vector_fields:
        script_sources += f"cosineSimilarity(params.query_vector, '{i}') + "
    script_sources += "1"

    search_query = {
        "size": k,
        "query": {
            "bool": {
                "must": [
                    {
                        "script_score": {
                            "query": {"term": {"company": filter_company}},
                            "script": {
                                "source": script_sources,
                                "params": {"query_vector": vector},
                            },
                        }
                    }
                ],
                "filter": {"term": {"company": filter_company}},
            }
        },
        "_source": source,
    }

    return search_query


def elastic_search_text_query(
    query: str,
    company: str,
    base_source: list[str],
    k: int = 5,
) -> list[dict]:
    search_query = {
        "size": k,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": base_source,
                        "type": "best_fields",
                    }
                },
                "filter": {"term": {"company": company}},
            }
        },
    }
    return search_query


def boost_source(
    boosting_dict: dict | None = None,
    base_source: list[str] | None = None,
) -> list[dict]:
    if not base_source:
        base_source = ["reporting_period", "filing_type", "section", "text"]

    if boosting_dict:
        for i in range(len(base_source)):
            if base_source[i] in boosting_dict:
                try:
                    base_source[i] = base_source[i] + "^" + boosting_dict[base_source[i]]
                except KeyError:
                    print(f"Boosting value not found for {base_source[i]}")
                    pass
    return base_source


def search(
    search_client: Elasticsearch,
    search_query: dict,
    index_name: str = "sec-filing-index",
    return_raw: bool = False,
) -> list[dict]:
    """
    Searches the vector DB for the given query.

    Args:
        search_client (Elasticsearch): Elasticsearch client.
        search_query (dict): Query to search for.
        index_name (str, optional): Index name. Defaults to "sec-filing-index".

    Returns:
        list[dict]: Search results.
    """
    search_results = search_client.search(index=index_name, body=search_query)

    if return_raw:
        return search_results
    else:
        result_sources = []
        for i in search_results["hits"]["hits"]:
            result_sources.append(i["_source"])
        return result_sources
