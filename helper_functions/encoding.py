import torch
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
from transformers import BertModel
from transformers import BertTokenizer


class FinBertEmbedder:
    def __init__(self, model_name="ProsusAI/finbert"):
        """
        Initializes the FinBertEmbedder class with the FinBERT model and tokenizer.

        Args:
        model_name (str): The name of the pre-trained FinBERT model. Default is 'ProsusAI/finbert'.
        """  # noqa: E501
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)

    def encode(self, text: str):
        """
        Encodes a given text into a FinBERT embedding.

        Args:
        text (str): The input text to be embedded.

        Returns:
        np.ndarray: The sentence embedding (average of token embeddings).
        """
        # Tokenize the input text
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, padding=True, max_length=512
        )

        # Pass the input through the model
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Get the last hidden state
        last_hidden_states = outputs.last_hidden_state

        # Pool the embeddings (mean of token embeddings)
        sentence_embedding = last_hidden_states.mean(dim=1).squeeze()

        return sentence_embedding


def encode_documents(
    documents: list[dict],
    embedding_model: SentenceTransformer | FinBertEmbedder,
) -> list[dict]:
    """
    Encode documents using a SentenceTransformer model.

    Args:
        documents (list[dict]): Documents to encode.
        embedding_model (SentenceTransformer | Any): embedding model to use.

    Returns:
        list[dict]: Documents with encoded vectors.
    """
    embeddings = []

    for doc in tqdm(documents):
        doc["text_vector"] = embedding_model.encode(doc["text"]).tolist()
        doc["non_text_vector"] = embedding_model.encode(
            doc["company"]
            + " "
            + doc["reporting_period"]
            + " "
            + doc["filing_type"]
            + " "
            + doc["section"]
        ).tolist()
        doc["all_vector"] = embedding_model.encode(
            doc["company"]
            + " "
            + doc["reporting_period"]
            + " "
            + doc["filing_type"]
            + " "
            + doc["section"]
            + " "
            + doc["text"]
        ).tolist()
        embeddings.append(doc)

    return embeddings
