import yaml
import json
from Scraper.web_scrape import scrape_corpus_from_src
from Chunking.chunker import semantic_chunking
from Embedding.embedding import embed
from Embedding.connection import recreate_vector_store
from dotenv import load_dotenv
import argparse


def ingest(config):
    print("Ingestion pipeline has begun")
    # Fetching the Corpus of SEC
    for source in config['sources']:
        print(f"Scraping the source : {source}")
        scrape_params = config[source]
        corpus = scrape_corpus_from_src(scrape_params["user"], scrape_params["url"], \
                               scrape_params["pattern"], scrape_params["n"], \
                                scrape_params["required_metadata"])
        # Fetching the corpus from corpus.json
        # with open("Corpus.json", 'r') as file:
        #     corpus = json.load(file)
        chunks = semantic_chunking(corpus)
        print(f"Final number of chunks extracted from corpus : {len(chunks)}")
        if config['Embeddings']['recreate_vector_store']:
            recreate_vector_store()
        embed(chunks)


def main():
    
    print("Hello from Retail - Investor Copilot!")
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--runtype", type=str, required=True, 
                        choices = ['RAG', 'INGEST', 'EVAL'],
                        help = "RAG - Retrieval/ Generation pipeline, " \
                        "INGEST - Indexing process (done once), EVAL - Evaluation periodically")


    args = parser.parse_args()
    runtype = args.runtype
    print(runtype)
    exit()
    # Fetching the config
    print("Fetching the parameters from the config")
    with open("config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if runtype == 'INGEST':
        ingest(config)



if __name__ == "__main__":
    main()
