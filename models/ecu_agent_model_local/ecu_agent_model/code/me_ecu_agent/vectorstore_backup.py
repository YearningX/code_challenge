"""Vectorstore Backup module."""

import os
from langchain_openai import OpenAIEmbeddings


def create_vector_stores(ecu_700_docs, ecu_800_docs):
    """
    Creates and returns two FAISS vector stores: one for ECU-700 and one for ECU-800.
    """
    embeddings = OpenAIEmbeddings()

    # Check if docs are empty to handle edge cases where directories might be missing or empty
    if ecu_700_docs:
        store_700 = FAISS.from_documents(ecu_700_docs, embeddings)
    else:
        store_700 = None

    if ecu_800_docs:
        store_800 = FAISS.from_documents(ecu_800_docs, embeddings)
    else:
        store_800 = None

    return store_700, store_800


def save_vector_stores(store_700, store_800, save_dir: str):
    """
    Saves the vector stores to disk.
    """
    if store_700:
        store_700.save_local(os.path.join(save_dir, "ecu_700_index"))

    if store_800:
        store_800.save_local(os.path.join(save_dir, "ecu_800_index"))


def load_vector_stores(load_dir: str):
    """
    Loads vector stores from the disk if they exist.
    """
    embeddings = OpenAIEmbeddings()
    store_700 = None
    store_800 = None

    path_700 = os.path.join(load_dir, "ecu_700_index")
    if os.path.exists(path_700):
        store_700 = FAISS.load_local(path_700, embeddings, allow_dangerous_deserialization=True)

    path_800 = os.path.join(load_dir, "ecu_800_index")
    if os.path.exists(path_800):
        store_800 = FAISS.load_local(path_800, embeddings, allow_dangerous_deserialization=True)

    return store_700, store_800
