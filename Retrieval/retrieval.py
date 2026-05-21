from langchain_huggingface import HuggingFaceEmbeddings
import os
import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# Moving code outside that needn't be doen every time a query is hit
emb_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        encode_kwargs={"normalize_embeddings": True}
    )

cluster_url = os.getenv("WEAVIATE_URL")
api_key = os.getenv("WEAVIATE_API_KEY")
# Connect to Weaviate Cloud
weaviate_client = weaviate.connect_to_weaviate_cloud(
        cluster_url = cluster_url, 
        auth_credentials=weaviate.auth.AuthApiKey(api_key)
    )


def retrieve(raw_query):
    print(f"Retrieving context to answer the query")
    
    query_instruction="Represent this sentence for searching relevant passages: "
    query = query_instruction + raw_query
    # print(emb_model.embed_query(query))

    
    # Step 2 — create vector store (embedding goes here)
    index = "Finance_corpus_for_rag"
    vector_store = WeaviateVectorStore(
    client=weaviate_client,
    index_name= index,
    text_key="text",
    embedding=emb_model
    )

    results = vector_store.similarity_search(
    query,
    k=5,
    alpha=0.8
    )
    weaviate_client.close()
    return results

def generate(raw_query, results):
    print(f"Generating the answer the query")
    # Format the chunks
    chunk_text = ""
    for i, doc in enumerate(results, 1):
        text = f"\nChunk_{i}: Text : {doc.page_content}"
        meta = f"\n Metadata : [Document Name : {doc.metadata['document_name']}, \
            Section : {doc.metadata['section_title']}, Page Number : {doc.metadata['start_page']}]\n"
        context = text + meta
        chunk_text += context
    with open('Retrieval/generate_prompt.txt', 'r') as f:
        prompt = f.read()
    prompt = PromptTemplate(
        template = prompt,
        input_variables = ['raw_query', 'chunks']
    )
    input_var = {'raw_query': raw_query, 'chunks': chunk_text}

    llm = ChatOllama(model = 'llama3.1')

    parser = StrOutputParser()

    chain = prompt | llm | parser

    response = chain.invoke(input_var)
    
    print(f"User : {raw_query} ")
    print(f"Copilot : {response} ")
