import hashlib
import re


def generate_document_id(text: str):
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    url_id = hash_hex[:8]
    return url_id


# def remove_thousands_commas(text):
#     """Removes commas used as thousands separators in numbers, but not in other contexts."""  # noqa: E501
#     # This regex matches only numbers with commas as thousands separators (not followed by letters)  # noqa: E501
#     # e.g., "1,000", "12,345.67", but not "1,000 people"
#     # It will match numbers with commas as thousands separators and will preserve commas in non-numeric contexts.  # noqa: E501
#     text = re.sub(r'(?<=\d),(?=\d)(?=\s|[^\d])', '', text)
#     return text


def print_long_text(text: str, line_length: int = 200):
    for i in range(0, len(text), line_length):
        print(text[i : i + line_length])
