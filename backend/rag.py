import logging
from sentence_transformers import SentenceTransformer, util
import faiss
import numpy as np
import openai
from collections import defaultdict
from transformers import pipeline

class RAG:
    def __init__(self, knowledge_base, openai_api_key, top_k=5, max_tokens=150):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.knowledge_base = knowledge_base
        self.index = self.create_index(knowledge_base)
        openai.api_key = openai_api_key
        self.cache = defaultdict(list)
        self.top_k = top_k
        self.max_tokens = max_tokens
        logging.basicConfig(level=logging.INFO)
        self.query_processor = pipeline("question-answering")

    def create_index(self, knowledge_base):
        embeddings = self.model.encode(knowledge_base, convert_to_tensor=True)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings))
        return index

    def retrieve(self, query, top_k=None):
        top_k = top_k or self.top_k
        if query in self.cache:
            logging.info(f"Cache hit for query: {query}")
            return self.cache[query]
        logging.info(f"Retrieving documents for query: {query}")
        try:
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            D, I = self.index.search(np.array([query_embedding]), top_k)
            retrieved_docs = [self.knowledge_base[i] for i in I[0]]
            self.cache[query] = retrieved_docs
            return retrieved_docs
        except Exception as e:
            logging.error(f"Error during retrieval: {e}")
            return []

    def hybrid_retrieve(self, query, top_k=5):
        # For simplicity, we use the existing dense retrieval method here
        return self.retrieve(query, top_k)

    def process_query(self, query):
        # Use a question-answering model to process the query
        result = self.query_processor(question=query, context=" ".join(self.knowledge_base))
        return result['answer']

    def generate_response(self, query, top_k=None, max_tokens=None):
        processed_query = self.process_query(query)
        top_k = top_k or self.top_k
        max_tokens = max_tokens or self.max_tokens
        retrieved_docs = self.hybrid_retrieve(processed_query, top_k)
        prompt = self.create_prompt(processed_query, retrieved_docs)
        try:
            response = openai.Completion.create(
                engine="davinci-codex",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                stop=["\n\n"]
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logging.error(f"Error during response generation: {e}")
            return "An error occurred while generating the response."

    def create_prompt(self, query, retrieved_docs):
        prompt = f"Query: {query}\n\n"
        prompt += "Retrieved Information:\n"
        for doc in retrieved_docs:
            prompt += f"- {doc}\n"
        prompt += "\nGenerate an insightful response based on the query and the retrieved information. "
        prompt += "Provide your answer strictly in JSON format with the keys 'answer' (the detailed response) and 'sources' (the list of supporting sentences)."
        return prompt

# Example usage
if __name__ == "__main__":
    knowledge_base = ["This is a sample sentence.", "Another example sentence.", "More knowledge here."]
    openai_api_key = "OPENAI_API_KEY"
    rag = RAG(knowledge_base, openai_api_key)
    print(rag.generate_response("sample query"))
