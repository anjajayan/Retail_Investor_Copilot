import os
import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore

from langchain_huggingface import HuggingFaceEmbeddings




def embed(docs):

    emb_model = HuggingFaceEmbeddings(
        model_name = "BAAI/bge-large-en-v1.5", 
         encode_kwargs={"normalize_embeddings": True}
    
    )
    cluster_url = os.getenv("WEAVIATE_URL")
    api_key = os.getenv("WEAVIATE_API_KEY")

    # Connect to Weaviate Cloud
    weaviate_client = weaviate.connect_to_weaviate_cloud(
        cluster_url = cluster_url, 
        auth_credentials=weaviate.auth.AuthApiKey(api_key)
    )

    # Step 2 — create vector store (embedding goes here)
    index = "Finance_corpus_for_rag"
    vector_store = WeaviateVectorStore(
    client=weaviate_client,
    index_name= index,
    text_key="text",
    embedding=emb_model
    )
    print(f"Adding Chunk documents into vector store collection : {index}")
    try:
        vector_store.add_documents(docs)
    finally:
        weaviate_client.close()


