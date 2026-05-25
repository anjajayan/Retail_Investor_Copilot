# Import Ragas components 
from ragas.llms import LangchainLLMWrapper
from ragas import evaluate
from ragas.metrics import Faithfulness, ContextPrecision
from ragas.run_config import RunConfig

import os
import weaviate
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
from Retrieval.retrieval import retrieve, generate
from ragas.dataset_schema import SingleTurnSample
from ragas import EvaluationDataset
import random
import pandas as pd


class GeneratorOutput(BaseModel):
    question: str = Field("The question created by the model on the input text")
    ground_truth: str = Field("The answer to the question, created from the inpput text")

class GeneratorList(BaseModel):
    lists: List[GeneratorOutput] = Field("The list of pairs of question and ground truths")

def run_evaluation():
    # model = ChatOllama(model = "llama3.1")

    # emb_model = HuggingFaceEmbeddings(
    #         model_name="BAAI/bge-large-en-v1.5",
    #         encode_kwargs={"normalize_embeddings": True}
    #     )
    

    # generator = TestsetGenerator(
    #     llm=LangchainLLMWrapper(model), 
    #     embedding_model=LangchainEmbeddingsWrapper(emb_model)
    # )

    # Get chunks from weaviate

    cluster_url = os.getenv("WEAVIATE_URL")
    api_key = os.getenv("WEAVIATE_API_KEY")
    # Connect to Weaviate Cloud
    weaviate_client = weaviate.connect_to_weaviate_cloud(
            cluster_url = cluster_url, 
            auth_credentials=weaviate.auth.AuthApiKey(api_key)
        )
    index = "Finance_corpus_for_rag"
    collections = weaviate_client.collections.get(index)
    response = collections.query.fetch_objects(
        limit = 100,
        return_properties=["text", "document_name", "document_type", "rule_number", "author", "created_date", "last_modified",
                            "is_amendment", "section_title", "chunk_index", "start_page", "end_page", "title"]
    )

    chunks = [
    Document(
        page_content=obj.properties['text'],
        metadata={
            'document_name': obj.properties['document_name'],
            'section_title': obj.properties['section_title'],
            'author': obj.properties['author'],
            'document_type': obj.properties['document_type'],
            'created_date': obj.properties['created_date'],
            'rule_number': obj.properties['rule_number'],
            'last_modified': obj.properties['last_modified'],
            'is_amendment': obj.properties['is_amendment'],
            'chunk_index': obj.properties['chunk_index'],
            'start_page': obj.properties['start_page'],
            'end_page': obj.properties['end_page'],
            'title': obj.properties['title'],
        }
    )
    for obj in response.objects
    ]
    print(f"Total chunks fetched: {len(chunks)}")
    # Generate the test set
    testset_generator(chunks)

    weaviate_client.close()

    
    # # Pass the chunks to the generator
    # try:
    #     dataset = generator.generate_with_langchain_docs(
    #         chunks,
    #         testset_size=5,
    #         query_distribution=[
    #             (SingleHopSpecificQuerySynthesizer(llm=LangchainLLMWrapper(model)), 0.75),   
    #             (MultiHopAbstractQuerySynthesizer(llm=LangchainLLMWrapper(model)), 0.25),   
    #         ]
    #     )
    # finally:
    #     pass
    # test_set = dataset.to_pandas()
    # print(test_set.head())


    
def testset_generator(chunks):
    # Create a semi-automated question generator
    # 
    # Single chunk - question 
    n = 1 # The number of questions per chunk
    generator = ChatOllama(model = "llama3.1")
    # Create the prompt
    with open('Evaluation/test_set_single_prompt.txt', 'r', encoding = 'utf-8') as f:
        prompt = f.read()
    
    prompt = PromptTemplate(
        template = prompt,
        input_variables = ['n', 'chunk_text']
    )

    # Create the structured output
    structured_generator = generator.with_structured_output(GeneratorList)

    chain = prompt | structured_generator 
    samples = []
    sample_chunks = random.sample(chunks, 20)
    counter = 1
    for chunk in sample_chunks:
        chunk_text = chunk.page_content
        print(f"Generating questions for chunk no. : {counter}")
        response = chain.invoke({'n': n, 'chunk_text': chunk_text})
        if not response.lists or isinstance(response.lists[0], str):
            print("Skipping malformed chunk response")
            continue
        for qn in response.lists:
            if isinstance(qn, str):
                print(f"Skipping malformed question")
                continue
            question = qn.question
            ground_truth = qn.ground_truth

            # Retrieve 
            retrieved_chunks = retrieve(question)
            contexts = [doc.page_content for doc in retrieved_chunks]
            generated_answer = generate(question, retrieved_chunks)
            sam = SingleTurnSample(user_input = question,
                retrieved_contexts = contexts,
                reference_contexts= [ground_truth],
                reference = ground_truth
                response = generated_answer)
            samples.append(sam)
    
    dataset = EvaluationDataset(samples=samples)
    # Saving to disk
    dataset.to_pandas().to_csv('Evaluation/Evaluation dataset.csv', index = False)

    # df = pd.read_csv('Evaluation/Evaluation dataset.csv')
    # samples = []
    # for _, row in df.iterrows():
    #     sam = SingleTurnSample(
    #         user_input=row['user_input'],
    #         retrieved_contexts=eval(row['retrieved_contexts']),
    #         reference_contexts=eval(row['reference_contexts']),
    #         reference=eval(row['reference_contexts'])[0],
    #         response=row['response']
    #     )
    #     samples.append(sam)

    dataset = EvaluationDataset(samples=samples)
    # Evaluate 
    evaluator_llm = LangchainLLMWrapper(generator)

    results = evaluate(
    dataset=dataset,
    metrics=[Faithfulness(llm=evaluator_llm), 
             ContextPrecision(llm=evaluator_llm)],
    run_config=RunConfig(timeout=300, max_workers=1,  max_retries=3)  # increase to 120 seconds
    
    )

    print(f"Results of the evaluation : {results}")





    