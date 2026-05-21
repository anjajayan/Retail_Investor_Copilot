from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from datetime import datetime

from itertools import groupby
from operator import itemgetter
import re
import pandas as pd
import numpy as np
from transformers import AutoTokenizer

def semantic_chunking(corpus):
    tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-en-v1.5")
    emb_model = HuggingFaceEmbeddings(
    model_name = "BAAI/bge-small-en-v1.5",
    )

    # Semantic chunking
    chunker = SemanticChunker(
    emb_model,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
    ) 
    final_chunks = []
    repl = False
    for document in corpus:
        for chunk in document:
            doc = Document(
                page_content=chunk['text'],
                metadata=chunk["metadata"]
                )
            tokens = len(tokenizer.encode(chunk['text']))
            if tokens > 512:
                print(f"Applying Semantic chunking on Long chunk: {tokens} tokens — {chunk['metadata']['section_title']}")
                semantic_chunk = chunker.split_documents([doc])
            else:
                semantic_chunk = [doc]
            final_chunks.extend(semantic_chunk)
    
    return final_chunks


def document_chunking(global_headers, metadata):
    
    # store the first text as heading by default
    i = 0
    chunks = []
    chunk_text = {"metadata": {}}
    # First line always doesn't to be heading
    if global_headers[0]['header'] == 0:
        chunk_text['metadata']['section_title'] = "Preamble"
    no_of_chunks = 0
    
    
    while i < len(global_headers):
        chunk_str = ""
        chunk_text = {"metadata": {}}

        if global_headers[i]['header'] == 1:
            
            chunk_text['metadata']['section_title'] = global_headers[i]['text']
            chunk_text['metadata']['start_page'] = global_headers[i]['page_no']
            # Do we need the header in the chunk too?
            chunk_str += " " + global_headers[i]['text']

            i += 1
        if 'section_title' not in chunk_text['metadata']:
            chunk_text['metadata']['section_title'] = "Preamble"
        while i < len(global_headers) and global_headers[i]['header'] == 0:
            
            chunk_str += " " + global_headers[i]['text']
            i += 1
        
        # chunk shouldnt have no text other than heading and should have greater than 100 characters
        # for it to be relevant enough
        if chunk_str and chunk_str != chunk_text['metadata']['section_title'] \
            and len(chunk_str) >= 100 :
            no_of_chunks +=1
            chunk_text['text'] = chunk_str

            chunk_text['metadata']['chunk_index'] = no_of_chunks
            chunk_text['metadata']['end_page'] = global_headers[i-1]['page_no']
            
            chunk_text['metadata'] = add_metadata(metadata, chunk_text['metadata'] )
            chunks.append(chunk_text)
        
    
    return chunks

def convert_date(date_str):
    date_str = date_str.removeprefix("D:").replace("'", "")
    dt = datetime.strptime(date_str, "%Y%m%d%H%M%S%z")
    return dt.isoformat()

def add_metadata(md, chunk_md):
    chunk_md['document_name'] = md['url'].split('/')[-1]
    chunk_md['title'] = md['Title']
    chunk_md['author'] = md['Author']
    chunk_md['created_date'] = convert_date(md['CreationDate'])
    chunk_md['last_modified'] = convert_date(md['ModDate'])
    chunk_md['document_type'] = None
    chunk_md['rule_number'] = None
    chunk_md['is_amendment'] = None
    
    # Structure of the metadata  
    # Document level
    # "document_name":   "FINRA_Rule_4512.pdf",
    # "document_type":   "FINRA_Rule",
    # "rule_number":     "4512",
    # "author":          "FINRA",
    # "date":            "2023-01-15",
    # "is_amendment":    False,

    # # Section level
    # "section_title":   "Customer Account Information",

    # # Chunk level
    # "chunk_index":     3,
    # "start_page":      12,
    # "end_page":        12,


    return chunk_md

def detect_headers(page, global_headers):
    
    # Detect the boundaries and structure in the document
    # 0. remove the footer
    if page.rects: 
        page_width = page.width
        # there could be rects which are just under-lines, and if is the only line present
        footer_line = max( # If the width of the rect > 50% of the page, then only it is a footer
                (r for r in page.rects if r['width'] > page_width * 0.5),
                key=lambda r: r['width'],
                default=None)
        footer_top = footer_line['top']  if footer_line else np.inf
    else:    
        footer_top = np.inf
    # 1. Extract the lines from each page. 
    words = page.extract_words(extra_attrs= ['fontname', 'size'])
    group = groupby(words, key=itemgetter('top'))
    lines = {key : [val for val in stuff] for key, stuff in group if key < footer_top } 
    # 2. Detect the headings
    
    
    for key,val in lines.items():
        header_flag = 0
        text = ""
        text = " ".join([v['text'] for v in val])
        # condition 1: if heading contains roman numeral/ alphabets or numbers followed by .
        # condition 2: if fontname contains bold in it
        roman_numbers = r'^([IVXLCDM]+|[A-Z]|\d+)\.\s'
        if re.match(roman_numbers, text) or text.isupper() or  all(['BOLD' in v['fontname'].upper() for v in val]):
            header_flag = 1
        global_headers.append({"text": text, "header": header_flag, "page_no": page.page_number})
    
    
        
    return global_headers