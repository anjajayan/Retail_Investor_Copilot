import requests
from bs4 import BeautifulSoup
import pdfplumber
import json
import io
import os


os.makedirs("Documents", exist_ok=True)

def scrape_corpus_from_src(user, url, pattern, n, required_metadata):
    session = requests.Session()
    session.headers.update({
        "User-Agent": user,
        # "Accept-Encoding": "gzip, deflate",
        # "Host": "data.sec.gov"
    })


    response = session.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    urls = [link.text for link in soup.find_all('loc') if pattern in link.text]
    # with open('urls.txt', 'w', encoding="utf-8") as f:
    #     f.write('\n'.join(urls))
    print(f"Fetched a total of {len(urls)} urls with the pattern : {pattern}")
    
    corpus = []
    counter = 0
    for links in urls[:n]:
        doc_info = scrape_document(session, links, required_metadata, counter) 
        counter += 1
        corpus.append(doc_info)
    print("Fetching process finished. Storing corpus into json")
    with open('Corpus.json', 'w', encoding="utf-8") as f:
        json.dump(corpus, f, indent=2)
    return corpus



def scrape_document(session, links, required_metadata, counter):
    
    response = session.get(links, timeout=30)
    # Saving the bytes object
    content = io.BytesIO(response.content)
    # Saving PDFs locally for evaluation and ground truth verification
    with open(f"Documents/Doc_{counter+1}.pdf", "wb") as f:
        f.write(content.getvalue())
    
    
    doc_info = []
    pdf =  pdfplumber.open(content)   
    print(f"Fetching document no. {counter + 1} with {len(pdf.pages)} pages from SEC")
    # Fetching metadata of the document
    metadata = {}
    
    for md in required_metadata:
        metadata[md] = pdf.metadata.get(md, "")
    metadata['url'] = links
    # Fetching and creating page level data
    for page_number, page in enumerate(pdf.pages, start=1):
        page_dict = {}
        page_dict['text'] = page.extract_text()
        metadata['page_number'] = page_number
        page_dict['metadata'] = metadata.copy()
        page_number += 1
        doc_info.append(page_dict)
    return doc_info
    
    

