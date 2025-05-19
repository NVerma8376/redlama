import json
import faiss
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class LightRAG:
    def __init__(self,
                 embedding_model_name='all-mpnet-base-v2',  # Changed to better model
                 llm_model_name='google/flan-t5-large',
                 top_k=5):  # Reduced to get more relevant results
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
        self.llm = AutoModelForSeq2SeqLM.from_pretrained(llm_model_name)
        self.top_k = top_k
        self.index = None
        self.entries = []

        # Add special token handling
        self.tokenizer.add_special_tokens({
            'additional_special_tokens': ['[THONTOR]']
        })
        self.llm.resize_token_embeddings(len(self.tokenizer))

    def load_knowledge_base(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.entries = data

        # Create more focused passages
        passages = []
        for entry in self.entries:
            # Add title as separate passage for better relevance
            passages.append(f"title: {entry['title']}")
            # Add transcript with clear formatting
            passages.append(f"transcript: {entry['transcript'][:300]}")  # Reduced length

        embeddings = self.embedding_model.encode(
            passages,
            convert_to_numpy=True,
            show_progress_bar=True,
            normalize_embeddings=True,
            batch_size=16  # Added batch processing
        )

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        print(f"✅ Indexed {len(self.entries)} transcripts.")

    def retrieve_context(self, query):
        try:
            # Create more specific query prompts
            query_variants = [
                f"question: {query}",
                f"how to {query}",
                f"what is {query}"
            ]

            # Get embeddings for all variants
            query_embeddings = self.embedding_model.encode(
                query_variants,
                convert_to_numpy=True
            )

            # Search with multiple variants
            distances_list = []
            indices_list = []
            for embedding in query_embeddings:
                distances, indices = self.index.search(
                    np.array([embedding]),
                    self.top_k
                )
                distances_list.append(distances[0])
                indices_list.append(indices[0])

            # Combine and sort results
            combined_distances = np.concatenate(distances_list)
            combined_indices = np.concatenate(indices_list)
            sorted_indices = combined_indices[np.argsort(combined_distances)]

            # Get unique entries
            unique_indices = []
            seen = set()
            for idx in sorted_indices:
                if idx not in seen:
                    unique_indices.append(idx)
                    seen.add(idx)
                    if len(unique_indices) >= self.top_k:
                        break

            return [self.entries[i] for i in unique_indices]
        except Exception as e:
            print(f"Error in retrieve_context: {str(e)}")
            return []

    def generate_answer(self, query):
        try:
            query = query.strip()
            if not query:
                return "Please ask a valid question."

            top_entries = self.retrieve_context(query)
            if not top_entries:
                return "No relevant context found for your question."

            # Create more focused context
            context_chunks = []
            for entry in top_entries:
                title = entry['title']
                transcript = entry['transcript'][:300]
                context_chunks.append(f"""
Title: {title}
Transcript: {transcript}
""")

            context = "\n".join(context_chunks)

            # More specific prompt with role definition
            prompt = f"""
You are a Python expert and teacher.
Based on the following transcript text, answer the question clearly and helpfully.
Focus on providing practical, step-by-step guidance.
Transcript context:
{context}
Question: {query}
Answer:
"""

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding="max_length"
            )

            # Improved generation parameters
            outputs = self.llm.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=150,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7,  # Reduced for more focused answers
                num_beams=4,
                no_repeat_ngram_size=3,
                early_stopping=True  # Added to prevent incomplete answers
            )

            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return answer.strip()

        except Exception as e:
            print(f"Error in generate_answer: {str(e)}")
            return "Sorry, I encountered an error while generating your answer."
if __name__ == "__main__":
    rag = LightRAG()
    rag.load_knowledge_base('video_dataset.json')

    print("\n🧠 YouTube Transcript AI (type 'exit' to quit)")
    while True:
        user_query = input("\nAsk a question: ").strip()
        if user_query.lower() == 'exit':
            break
        response = rag.generate_answer(user_query)
        print("\nAnswer:\n", response)
