import os
import weaviate
import weaviate.classes.config as wc


def recreate_vector_store():
    cluster_url = os.getenv("WEAVIATE_URL")
    api_key = os.getenv("WEAVIATE_API_KEY")

    # Connect to Weaviate Cloud
    weaviate_client = weaviate.connect_to_weaviate_cloud(
        cluster_url = cluster_url, 
        auth_credentials=weaviate.auth.AuthApiKey(api_key)
    )

    # ONE TIME - Create a collection
    weaviate_client.collections.delete("Finance_corpus_for_rag")
    print(f"Creating Collection - Finance_corpus_for_rag in Weaviate")
    weaviate_client.collections.create(
    name="Finance_corpus_for_rag",
    vectorizer_config=wc.Configure.Vectorizer.none(),
    properties=[
        wc.Property(name="text", data_type=wc.DataType.TEXT),
        wc.Property(name="document_name", data_type=wc.DataType.TEXT),
        wc.Property(name="document_type", data_type=wc.DataType.TEXT),
        wc.Property(name="rule_number", data_type=wc.DataType.TEXT),
        wc.Property(name="author", data_type=wc.DataType.TEXT),
        wc.Property(name="created_date", data_type=wc.DataType.DATE),
        wc.Property(name="last_modified", data_type=wc.DataType.DATE),
        wc.Property(name="is_amendment", data_type=wc.DataType.BOOL),
        wc.Property(name="section_title", data_type=wc.DataType.TEXT),
        wc.Property(name="chunk_index", data_type=wc.DataType.INT),
        wc.Property(name="start_page", data_type=wc.DataType.INT),
        wc.Property(name="end_page", data_type=wc.DataType.INT),
        wc.Property(name="title", data_type=wc.DataType.TEXT),
    ]
    )
    weaviate_client.close()