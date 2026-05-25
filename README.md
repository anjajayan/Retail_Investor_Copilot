# RAG-Powered Investor Copilot

A RAG-powered copilot that helps retail investors understand SEC and FINRA regulations by answering their questions in plain English, grounded in official regulatory documents. It acknowledges this gap and fills it by breaking down SEC rules and regulations into layman's terms — with citations.

- **Target user:** Retail investors with limited financial background
- **Core job:** Answer regulation- and protection-related questions using official sources
- **Source scope (v1):** SEC investor education/guidance
- **Out of scope:** Personalised investment advice, portfolio recommendations, tax advice, legal advice

---

## Key Highlights

- **Hierarchical chunking pipeline** with document-aware PDF parsing
- **Hybrid semantic + keyword search** using Weaviate Cloud
- **Fully local generation** using Ollama (Llama 3.1)
- **Evaluated using RAGAS** — Context Precision: **0.86**

---

## Architecture

<img width="124" height="150" alt="retail_investor_copilot_architecture" src="https://github.com/user-attachments/assets/92d39fd9-ab07-4e12-94c4-bf63ff70d979" />

---

## How It Works

The copilot system operates in **3 core modes**:

### 1. Ingestion Mode
Ingestion begins with scraping SEC regulatory documents and parsing the retrieved PDFs. The corpus is chunked through **document structure-aware chunking**, where each document is divided into individual sections with important metadata attached to enable citation awareness. For sections exceeding the 512-token context window, chunks are further broken down via **semantic chunking**. These chunks are stored in a Weaviate Cloud collection.

### 2. Retrieval-Generation Mode
Retrieval begins with a user query that is embedded and used for **Weaviate hybrid search**. Both BM25 and semantic search are employed, and the retrieved chunks are passed to the LLM as context. The LLM then generates a simplified, plain-English explanation for the user.

### 3. Evaluation Mode
The evaluation pipeline involves generating a test dataset using Ollama (Llama 3.1), which produces plain-English answers with citations. Evaluation is performed using the **RAGAS framework**, measuring faithfulness and context precision.

---

## How to Run

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Fill in your values in .env
   ```

4. **Run ingestion**
   ```bash
   python main.py --runtype INGST
   ```

5. **Ask a question**
   ```bash
   python main.py --runtype RAG
   ```

6. **Run evaluation**
   ```bash
   python main.py --runtype EVAL
   ```

---

## Evaluation Results

| Metric | Score |
|---|---|
| Context Precision | **0.86** |
| Faithfulness | inconclusive |

Context Precision of 0.86 indicates strong retrieval quality — the hybrid search pipeline consistently surfaces relevant chunks for user queries.

Faithfulness score was inconclusive due to local LLM timeout constraints during evaluation. This is a known limitation of running RAGAS with Ollama locally rather than a cloud LLM API.

Evaluation was conducted using RAGAS with Mixtral as the judge LLM due to API access constraints. Results should be interpreted as relative performance indicators rather than absolute quality scores.

Automated test set generation was attempted using the RAGAS `TestsetGenerator` with local Mixtral. Structured output compliance issues were encountered — a known limitation of open source models without API access. The pipeline was adapted to a semi-automated approach using Llama 3.1 for question generation with manual review.

---

## Limitations & Future Work

- Faithfulness evaluation requires a capable cloud LLM (e.g. GPT-4) for reliable scores
- Corpus currently limited to 5 SEC/FINRA documents — broader coverage planned for v2
- No REST API or UI layer yet — FastAPI endpoint and Streamlit UI planned
- Corpus audit and relevance review pending
- Document metadata enrichment (rule numbers, amendment flags) deferred to v2
