# # backend/services/rag_service.py
# import os
# import json
# import asyncio
# from typing import List, Dict, Any, AsyncGenerator, Optional
# import logging
# from pathlib import Path

# # LlamaIndex imports
# from llama_index.core import VectorStoreIndex, Document, Settings
# from llama_index.core.node_parser import SentenceSplitter
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.llms.ollama import Ollama
# from llama_index.vector_stores.chroma import ChromaVectorStore
# import chromadb

# logger = logging.getLogger(__name__)

# class RAGService:
#     def __init__(self):
#         self.index = None
#         self.query_engine = None
#         self.llm = None
#         self.embedding_model = None
#         self.chroma_client = None
#         self.collection = None

#     async def initialize(self):
#         """Initialize the RAG service with local models"""
#         try:
#             # Initialize embedding model (local)
#             self.embedding_model = HuggingFaceEmbedding(
#                 model_name="sentence-transformers/all-MiniLM-L6-v2"
#             )

#             # Initialize LLM (Ollama - assumes local installation)
#             self.llm = Ollama(model="llama3.1", request_timeout=60.0)

#             # Set global settings
#             Settings.embed_model = self.embedding_model
#             Settings.llm = self.llm
#             Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

#             # Initialize ChromaDB
#             self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
#             self.collection = self.chroma_client.get_or_create_collection("askhercare")

#             # Create vector store
#             vector_store = ChromaVectorStore(chroma_collection=self.collection)

#             # Load and index documents
#             await self._load_documents()

#             # Create index
#             self.index = VectorStoreIndex.from_vector_store(vector_store)

#             # Create query engine
#             self.query_engine = self.index.as_query_engine(
#                 similarity_top_k=5,
#                 response_mode="tree_summarize"
#             )

#             logger.info("RAG service initialized successfully")

#         except Exception as e:
#             logger.error(f"Failed to initialize RAG service: {str(e)}")
#             raise

#     async def _load_documents(self):
#         """Load medical documents from JSON dataset"""
#         try:
#             data_path = Path("./data/medical_qa_dataset.json")
#             if not data_path.exists():
#                 logger.warning("Medical dataset not found, creating sample data")
#                 await self._create_sample_dataset()

#             with open(data_path, 'r') as f:
#                 dataset = json.load(f)

#             documents = []
#             for item in dataset:
#                 # Create document with metadata
#                 doc = Document(
#                     text=f"Q: {item['question']}\\n\\nA: {item['answer']}",
#                     metadata={
#                         "category": item.get("category", "general"),
#                         "source": item.get("source", "medical_dataset"),
#                         "tags": item.get("tags", [])
#                     }
#                 )
#                 documents.append(doc)

#             # Check if collection is empty
#             if self.collection.count() == 0:
#                 # Add documents to index
#                 for doc in documents:
#                     self.index = VectorStoreIndex.from_documents([doc])
#                 logger.info(f"Loaded {len(documents)} documents into vector store")
#             else:
#                 logger.info("Vector store already contains documents")

#         except Exception as e:
#             logger.error(f"Error loading documents: {str(e)}")
#             raise

#     async def _create_sample_dataset(self):
#         """Create sample medical Q&A dataset"""
#         sample_data = [
#             {
#                 "question": "What is a normal menstrual cycle length?",
#                 "answer": "A normal menstrual cycle typically ranges from 21 to 35 days, with an average of 28 days. The menstrual period itself usually lasts 3-7 days. Cycles can vary from month to month and may change throughout your life.",
#                 "category": "menstruation",
#                 "tags": ["periods", "cycle", "normal"]
#             },
#             {
#                 "question": "What are the early signs of pregnancy?",
#                 "answer": "Early pregnancy signs include missed periods, nausea (morning sickness), breast tenderness, fatigue, frequent urination, food aversions or cravings, and mood changes. However, these symptoms can vary greatly between individuals.",
#                 "category": "pregnancy",
#                 "tags": ["pregnancy", "symptoms", "early signs"]
#             },
#             {
#                 "question": "What is PCOS and what are its symptoms?",
#                 "answer": "PCOS (Polycystic Ovary Syndrome) is a hormonal disorder affecting women of reproductive age. Symptoms include irregular periods, excess androgen levels (causing acne, hirsutism), polycystic ovaries, weight gain, and insulin resistance.",
#                 "category": "pcos",
#                 "tags": ["PCOS", "hormonal", "symptoms"]
#             },
#             {
#                 "question": "What birth control options are available?",
#                 "answer": "Birth control options include hormonal methods (pills, patches, rings, injections), barrier methods (condoms, diaphragms), IUDs (hormonal and copper), implants, and permanent methods (tubal ligation). Each has different effectiveness rates and side effects.",
#                 "category": "birth_control",
#                 "tags": ["contraception", "birth control", "family planning"]
#             },
#             {
#                 "question": "What should I expect during my first gynecological exam?",
#                 "answer": "Your first gynecological exam typically includes discussing your medical history, a physical exam, and possibly a pelvic exam depending on your age and needs. The doctor will explain each step and you can ask questions. It's normal to feel nervous.",
#                 "category": "first_time_sex",
#                 "tags": ["gynecological exam", "first time", "what to expect"]
#             },
#             {
#                 "question": "How can I maintain good vaginal health?",
#                 "answer": "Maintain vaginal health by practicing good hygiene (gentle washing with water), wearing breathable cotton underwear, avoiding douches and harsh soaps, staying hydrated, eating a balanced diet with probiotics, and practicing safe sex.",
#                 "category": "vaginal_health",
#                 "tags": ["hygiene", "vaginal health", "prevention"]
#             }
#         ]

#         # Ensure data directory exists
#         os.makedirs("./data", exist_ok=True)

#         with open("./data/medical_qa_dataset.json", 'w') as f:
#             json.dump(sample_data, f, indent=2)

#         logger.info("Created sample medical dataset")

#     async def get_response(
#         self,
#         question: str,
#         personality_mode: str = "doctor",
#         category: Optional[str] = None
#     ) -> Dict[str, Any]:
#         """Get RAG response for a question"""
#         try:
#             # Customize prompt based on personality mode
#             prompt = self._build_prompt(question, personality_mode, category)

#             # Query the RAG system
#             response = self.query_engine.query(prompt)

#             # Extract sources
#             sources = []
#             if hasattr(response, 'source_nodes'):
#                 for node in response.source_nodes:
#                     sources.append({
#                         "content": node.text[:200] + "..." if len(node.text) > 200 else node.text,
#                         "score": node.score if hasattr(node, 'score') else 0.8,
#                         "metadata": node.metadata
#                     })

#             return {
#                 "answer": str(response),
#                 "sources": sources,
#                 "confidence": 0.8  # Default confidence
#             }

#         except Exception as e:
#             logger.error(f"Error getting RAG response: {str(e)}")
#             return {
#                 "answer": "I'm sorry, I'm having trouble processing your question right now. Please try again or consult with a healthcare professional.",
#                 "sources": [],
#                 "confidence": 0.0
#             }

#     async def get_streaming_response(
#         self,
#         question: str,
#         personality_mode: str = "doctor",
#         category: Optional[str] = None
#     ) -> AsyncGenerator[Dict[str, Any], None]:
#         """Get streaming RAG response"""
#         try:
#             response = await self.get_response(question, personality_mode, category)

#             # Simulate streaming by yielding chunks
#             words = response["answer"].split()
#             current_chunk = ""

#             for i, word in enumerate(words):
#                 current_chunk += word + " "

#                 if i % 5 == 4 or i == len(words) - 1:  # Yield every 5 words
#                     yield {
#                         "chunk": current_chunk,
#                         "is_complete": i == len(words) - 1,
#                         "sources": response["sources"] if i == len(words) - 1 else []
#                     }
#                     current_chunk = ""
#                     await asyncio.sleep(0.1)  # Small delay for streaming effect

#         except Exception as e:
#             logger.error(f"Error in streaming response: {str(e)}")
#             yield {
#                 "chunk": "Sorry, I encountered an error processing your request.",
#                 "is_complete": True,
#                 "sources": []
#             }

#     def _build_prompt(self, question: str, personality_mode: str, category: Optional[str] = None) -> str:
#         """Build prompt based on personality mode and category"""
#         base_context = "You are a helpful assistant providing accurate medical information about women's health. Always recommend consulting healthcare professionals for serious concerns."

#         personality_contexts = {
#             "doctor": "Respond in a professional, medical tone with clinical accuracy. Use appropriate medical terminology while remaining accessible.",
#             "bestie": "Respond like a caring best friend who happens to be knowledgeable about health. Be warm, supportive, and use casual but accurate language.",
#             "sister": "Respond like a caring older sister who wants to help. Be gentle, understanding, and use reassuring language while providing accurate information."
#         }

#         category_context = ""
#         if category:
#             category_context = f"This question is related to {category.replace('_', ' ')}. "

#         prompt = f"{base_context} {personality_contexts.get(personality_mode, personality_contexts['doctor'])} {category_context}\\n\\nQuestion: {question}"

#         return prompt

#     async def simplify_response(self, text: str) -> str:
#         """Simplify medical response for teens"""
#         try:
#             simplify_prompt = f"""
#             Please rewrite the following medical information in simple, teen-friendly language.
#             Use everyday words instead of medical jargon, keep sentences short, and make it easy to understand for a teenager.

#             Original text: {text}

#             Simplified version:
#             """

#             response = self.llm.complete(simplify_prompt)
#             return str(response)

#         except Exception as e:
#             logger.error(f"Error simplifying response: {str(e)}")
#             return "Sorry, I couldn't simplify that right now. Please ask me to explain any words you don't understand!"

#     async def explain_medical_term(self, term: str) -> str:
#         """Explain medical terminology"""
#         try:
#             explain_prompt = f"""
#             Please explain the medical term "{term}" in simple, easy-to-understand language.
#             Include what it means, why it's important, and any context that would help someone understand it better.
#             Keep the explanation friendly and not scary.

#             Medical term: {term}

#             Explanation:
#             """

#             response = self.llm.complete(explain_prompt)
#             return str(response)

#         except Exception as e:
#             logger.error(f"Error explaining medical term: {str(e)}")
#             return f"I'm having trouble explaining '{term}' right now. You might want to ask your doctor or look it up in a medical dictionary."
