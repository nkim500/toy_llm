from elasticsearch import Elasticsearch
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from helper_functions import searching


def build_prompt(query: str, search_results: list, prompt_template: str = None) -> str:
    if prompt_template is None:
        prompt_template = """
            You are a financial analyst. Answer the QUESTION based on the CONTEXT.
            Use only the facts from the CONTEXT when answering the QUESTION.
            If the CONTEXT does not contain the answer, output a helpful message.

            QUESTION: {question}
            CONTEXT:
            {context}
        """
    context = ""
    for doc in search_results:
        context = (
            context
            + f"""
            period: {doc["reporting_period"]}\n filing_type:{doc["filing_type"]}\n text: {doc["text"]}\n section: {doc["section"]}\n\n
        """  # noqa: E501
        )
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt


def llm(prompt: str, model: str, llm_client: OpenAI) -> str:
    response = llm_client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def rag(
    query: str,
    search_query: dict,
    search_client: Elasticsearch,
    llm_client: OpenAI,
    retrieval_model: str = "moondream",
    prompt_template: str | None = None,
    index_name: str = "sec-filing-index",
) -> str:
    try:
        search_results = searching.search(
            search_client=search_client, search_query=search_query, index_name=index_name
        )
    except Exception as e:
        print(f"Search query did not return any results:\t{e}")
        return
    prompt = build_prompt(query, search_results, prompt_template)
    answer = llm(prompt, retrieval_model, llm_client)

    return answer
