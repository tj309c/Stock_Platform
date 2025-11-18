"""
download_nltk_data.py

Simple utility to download the NLTK data needed by TextBlob for sentiment
analysis. Run this once in the virtual environment used for the project to
ensure TextBlob lower-level resources (tokenizers, taggers) are available.
"""
from __future__ import annotations

import nltk


def download_data() -> None:
    """Download NLTK corpora required by TextBlob.

    TextBlob uses the 'punkt' tokenizer and the averaged perceptron tagger by
    default for sentence/word tokenization and basic POS tagging. The
    'wordnet' corpus is sometimes helpful for other NLP tasks (lemmatization)
    and we include it as optional convenience.
    """
    print("Downloading NLTK data required for TextBlob (punkt, averaged_perceptron_tagger, wordnet)...")
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')
    print("Download complete.")


if __name__ == '__main__':
    download_data()