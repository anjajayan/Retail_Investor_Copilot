import yaml
from Scraper.web_scrape import scrape_corpus_from_src

def main():
    print("Hello from Retail - Investor Copilot!")
    # Fetching the config
    print("Fetching the parameters from the config")
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Fetching the Corpus of SEC
    for source in config['sources']:
        print(f"Scraping the source : {source}")
        scrape_params = config[source]
        corpus = scrape_corpus_from_src(scrape_params["user"], scrape_params["url"], \
                               scrape_params["pattern"], scrape_params["n"], \
                                scrape_params["required_metadata"])
    
        
        




if __name__ == "__main__":
    main()
