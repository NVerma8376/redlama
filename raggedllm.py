import json
import faiss
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class LightRAG:
    def __init__(self, embedding_model_name='intfloat/e5-small-v2',
                 llm_model_name='google/flan-t5-small', top_k=5):
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
        self.llm = AutoModelForSeq2SeqLM.from_pretrained(llm_model_name)
        self.top_k = top_k
        self.index = None
        self.comment_texts = []

    def load_knowledge_base(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.comment_texts = [entry['comment'] for entry in data]
        passages = [f"passage: {text}" for text in self.comment_texts]
        embeddings = self.embedding_model.encode(passages, convert_to_numpy=True, show_progress_bar=True)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        print(f"Indexed {len(self.comment_texts)} comments.")

    def retrieve_context(self, query):
        query_embedding = self.embedding_model.encode([f"query: {query}"])
        distances, indices = self.index.search(query_embedding, self.top_k)
        return [self.comment_texts[i] for i in indices[0]]

    def generate_answer(self, query):
        context = self.retrieve_context(query)
        prompt = "Context:\n" + "\n".join(context) + f"\n\nQuestion: {query}\nAnswer:"
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.llm.generate(**inputs, max_new_tokens=150)
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer.strip()

if __name__ == "__main__":
    rag = LightRAG()
    rag.load_knowledge_base('iran_conflict_comments.json')  

    while True:
        user_query = input("\nAsk a question (or type 'exit'): ")
        if user_query.lower() == 'exit':
            break
        response = rag.generate_answer(user_query)
        print("\nAnswer:\n", response)
