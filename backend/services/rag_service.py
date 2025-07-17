# backend/services/rag_service_optimized.py
# Enhanced version that maximizes both AI and knowledge base

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(override=True)

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.medical_data = []
        self.initialized = False
        self.client = None
        self.use_ai = False

    async def initialize(self):
        """Initialize the service"""
        try:
            # Load medical data first
            await self._load_medical_data()

            # Try OpenAI initialization
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key.strip():
                try:
                    self.client = AsyncOpenAI(api_key=api_key)

                    # Quick test to verify connection
                    await self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5,
                    )

                    self.use_ai = True
                    logger.info(
                        "✅ OpenAI client initialized - using GPT-4o-mini with knowledge enhancement"
                    )

                except Exception as e:
                    logger.warning(f"OpenAI initialization failed: {e}")
                    self.use_ai = False
                    logger.info("Falling back to knowledge-based responses")
            else:
                logger.info("No OpenAI API key found - using knowledge-based responses")
                self.use_ai = False

            self.initialized = True
            ai_status = "AI-enhanced" if self.use_ai else "knowledge-based"
            logger.info(f"RAG service initialized successfully ({ai_status})")

        except Exception as e:
            logger.error(f"Initialization error: {e}")
            self.use_ai = False
            self.initialized = True
            logger.info("Using fallback knowledge-based responses")

    async def _load_medical_data(self):
        """Load medical Q&A data"""
        try:
            data_paths = [
                Path("./data/medical_qa_dataset.json"),
                Path("../data/medical_qa_dataset.json"),
                Path("./medical_qa_dataset.json"),
            ]

            dataset_loaded = False
            for data_path in data_paths:
                if data_path.exists():
                    with open(data_path, "r", encoding="utf-8") as f:
                        self.medical_data = json.load(f)
                    logger.info(f"📚 Loaded {len(self.medical_data)} medical Q&A pairs")
                    dataset_loaded = True
                    break

            if not dataset_loaded:
                logger.warning("Medical dataset not found")
                self.medical_data = []

        except Exception as e:
            logger.error(f"Error loading medical data: {e}")
            self.medical_data = []

    def _find_best_context(
        self, question: str, category: Optional[str] = None, top_k: int = 3
    ) -> str:
        """Find the most relevant medical context using advanced matching"""
        if not self.medical_data:
            return ""

        question_lower = question.lower()
        question_words = set(word.lower() for word in question.split() if len(word) > 2)

        scored_items = []

        for item in self.medical_data:
            score = 0

            # Category exact match (high priority)
            if category and item.get("category") == category:
                score += 2.0

            # Question similarity
            item_question = item.get("question", "").lower()
            item_words = set(
                word.lower() for word in item_question.split() if len(word) > 2
            )

            # Exact question match (highest priority)
            if question_lower in item_question or item_question in question_lower:
                score += 5.0

            # Word overlap in question
            common_words = question_words.intersection(item_words)
            if common_words:
                score += len(common_words) * 0.5

            # Answer content similarity
            item_answer = item.get("answer", "").lower()
            answer_words = set(
                word.lower() for word in item_answer.split() if len(word) > 2
            )
            common_answer_words = question_words.intersection(answer_words)
            if common_answer_words:
                score += len(common_answer_words) * 0.3

            # Tag matching
            item_tags = [tag.lower() for tag in item.get("tags", [])]
            for word in question_words:
                if any(word in tag for tag in item_tags):
                    score += 0.8

            if score > 0:
                scored_items.append((item, score))

        # Sort by score and get top results
        scored_items.sort(key=lambda x: x[1], reverse=True)
        top_items = scored_items[:top_k]

        # Format context
        context_parts = []
        for item, score in top_items:
            context_parts.append(f"Q: {item['question']}\nA: {item['answer']}")

        return "\n\n---\n\n".join(context_parts)

    async def get_response(
        self,
        question: str,
        personality_mode: str = "doctor",
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get enhanced response using AI + knowledge base"""
        if self.use_ai and self.client:
            return await self._get_ai_enhanced_response(
                question, personality_mode, category
            )
        else:
            return await self._get_knowledge_response(
                question, personality_mode, category
            )

    async def _get_ai_enhanced_response(
        self, question: str, personality_mode: str, category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get AI-enhanced response with knowledge base context"""
        try:
            # Get relevant medical context
            context = self._find_best_context(question, category, top_k=3)

            # Enhanced personality prompts
            personality_prompts = {
                "doctor": """You are a professional, knowledgeable healthcare assistant specializing in women's health. 
                Provide accurate, evidence-based medical information while being compassionate and professional. 
                Always recommend consulting healthcare professionals for personalized advice and serious concerns.
                Use clinical terminology appropriately but explain it clearly.""",
                "bestie": """You are a caring, supportive best friend who happens to be very knowledgeable about women's health. 
                Use warm, friendly, conversational language with appropriate emojis (but don't overuse them). 
                Be encouraging and supportive while providing accurate medical information. 
                Make complex topics feel approachable and less scary. Always encourage professional medical care when needed.""",
                "sister": """You are a loving, protective older sister who cares deeply about women's health and wellbeing. 
                Use gentle, reassuring, nurturing language that makes the person feel safe and supported. 
                Share information in a caring way that reduces anxiety while being medically accurate. 
                Emphasize self-care and the importance of advocating for one's health.""",
            }

            system_prompt = personality_prompts.get(
                personality_mode, personality_prompts["doctor"]
            )

            # Enhanced user prompt with better context integration
            if context:
                user_prompt = f"""Based on the following curated medical information about women's health, please answer the user's question.

MEDICAL KNOWLEDGE BASE:
{context}

USER QUESTION: {question}

Instructions:
- Use the medical knowledge base as your primary source when relevant
- Provide comprehensive, accurate information
- If the knowledge base doesn't fully answer the question, supplement with your medical knowledge
- Always recommend consulting healthcare professionals for personalized medical advice
- Be specific and helpful while maintaining appropriate medical disclaimers"""
            else:
                user_prompt = f"""Please answer this women's health question: {question}

Provide accurate, helpful medical information while always recommending consultation with healthcare professionals for personalized advice."""

            # Make API call with optimized parameters
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            answer = response.choices[0].message.content.strip()

            # Create enhanced sources
            sources = []
            if context:
                sources.append(
                    {
                        "content": "Curated medical knowledge base with clinical guidelines",
                        "score": 0.95,
                        "metadata": {
                            "source": "ai_enhanced_knowledge_base",
                            "model": "gpt-4o-mini",
                            "context_used": True,
                        },
                    }
                )
            else:
                sources.append(
                    {
                        "content": "AI medical knowledge with professional guidelines",
                        "score": 0.85,
                        "metadata": {
                            "source": "ai_general_knowledge",
                            "model": "gpt-4o-mini",
                            "context_used": False,
                        },
                    }
                )

            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.95 if context else 0.85,
            }

        except Exception as e:
            logger.error(f"AI enhancement error: {e}")
            # Fall back to knowledge-based response
            return await self._get_knowledge_response(
                question, personality_mode, category
            )

    async def _get_knowledge_response(
        self, question: str, personality_mode: str, category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fallback knowledge-based response"""
        # Find best matching content
        context = self._find_best_context(question, category, top_k=1)

        if context:
            # Extract the answer from context
            lines = context.split("\n")
            answer_text = ""
            for i, line in enumerate(lines):
                if line.startswith("A: "):
                    answer_text = line[3:]  # Remove "A: " prefix
                    break

            if answer_text:
                # Customize based on personality
                customized_answer = self._customize_knowledge_response(
                    answer_text, personality_mode, question
                )

                return {
                    "answer": customized_answer,
                    "sources": [
                        {
                            "content": "Medical knowledge database",
                            "score": 0.8,
                            "metadata": {"source": "knowledge_base", "matched": True},
                        }
                    ],
                    "confidence": 0.8,
                }

        # Generic response if no match found
        return self._get_generic_response(question, personality_mode)

    def _customize_knowledge_response(
        self, base_answer: str, personality_mode: str, question: str
    ) -> str:
        """Customize knowledge base responses by personality"""
        if personality_mode == "bestie":
            return f"Hey! Great question about this 💕 {base_answer} Hope this helps! Remember, you know your body best, so definitely talk to a healthcare provider if you have any concerns. You've got this! 🌟"
        elif personality_mode == "sister":
            return f"I'm so glad you asked about this! 🤗 {base_answer} Remember, every woman's experience is different, and it's always okay to seek professional medical advice when you need it. Take care of yourself! 💜"
        else:  # doctor mode
            return f"Regarding your question about {question.lower()}: {base_answer} I recommend discussing any specific concerns with your healthcare provider for personalized medical guidance."

    def _get_generic_response(
        self, question: str, personality_mode: str
    ) -> Dict[str, Any]:
        """Generic response when no specific knowledge is found"""
        responses = {
            "doctor": f"Thank you for your question about '{question}'. While I don't have specific information about this topic in my current knowledge base, I recommend consulting with a qualified healthcare provider who can provide personalized medical advice based on your individual circumstances.",
            "bestie": f"That's a really thoughtful question about '{question}'! 💕 I don't have specific info about this in my knowledge base right now, but I'd definitely suggest chatting with a healthcare provider who can give you the best advice for your unique situation. You're smart for asking! 🌟",
            "sister": f"I appreciate you asking about '{question}' - it shows you're taking care of your health! 🤗 While I don't have detailed information about this specific topic, I encourage you to speak with a healthcare professional who can provide you with accurate, personalized guidance. Never hesitate to advocate for your health! 💜",
        }

        return {
            "answer": responses.get(personality_mode, responses["doctor"]),
            "sources": [],
            "confidence": 0.5,
        }

    async def get_streaming_response(
        self,
        question: str,
        personality_mode: str = "doctor",
        category: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response in chunks"""
        try:
            response = await self.get_response(question, personality_mode, category)

            # Stream words in natural chunks
            words = response["answer"].split()
            current_chunk = ""

            for i, word in enumerate(words):
                current_chunk += word + " "

                # Send chunk every 3-5 words for natural feel
                if i % 4 == 3 or i == len(words) - 1:
                    yield {
                        "chunk": current_chunk,
                        "is_complete": i == len(words) - 1,
                        "sources": response["sources"] if i == len(words) - 1 else [],
                    }
                    current_chunk = ""
                    await asyncio.sleep(0.1)  # Natural pause

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {
                "chunk": "I'm having some trouble processing your request. Please try again.",
                "is_complete": True,
                "sources": [],
            }

    async def simplify_response(self, text: str) -> str:
        """Simplify medical response for teens"""
        if self.use_ai and self.client:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at explaining medical information in simple, teen-friendly language. Rewrite the given text using everyday words that a teenager would easily understand. Keep it accurate but make it easy to read. Use a warm, encouraging tone.",
                        },
                        {
                            "role": "user",
                            "content": f"Please simplify this medical text for a teenager: {text}",
                        },
                    ],
                    max_tokens=300,
                    temperature=0.5,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"AI simplification error: {e}")

        # Fallback simplification
        simplified = text
        medical_terms = {
            "syndrome": "condition",
            "hormonal disorder": "hormone problem",
            "reproductive age": "when you can have babies",
            "menstrual cycle": "period cycle",
            "gynecological": "women's health",
            "contraceptives": "birth control",
            "ovulation": "when your ovary releases an egg",
            "endometriosis": "when uterine tissue grows outside the uterus",
        }

        for medical_term, simple_term in medical_terms.items():
            simplified = simplified.replace(medical_term, simple_term)

        return f"Here's a simpler way to understand it: {simplified}"

    async def explain_medical_term(self, term: str) -> str:
        """Explain medical terminology"""
        if self.use_ai and self.client:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful medical educator. Explain medical terms in simple, clear language that anyone can understand. Focus on women's health topics. Be encouraging and not scary.",
                        },
                        {
                            "role": "user",
                            "content": f"Please explain the medical term '{term}' in simple language that's easy to understand, especially for women's health.",
                        },
                    ],
                    max_tokens=200,
                    temperature=0.5,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"AI explanation error: {e}")

        # Fallback explanations
        term_explanations = {
            "pcos": "PCOS stands for Polycystic Ovary Syndrome. It's a common condition where a woman's hormones are out of balance, which can cause irregular periods, weight gain, acne, and extra hair growth.",
            "ovulation": "Ovulation is when your ovary releases an egg each month, usually around the middle of your cycle. This is when you're most likely to get pregnant.",
            "menstruation": "Menstruation is your monthly period - when the lining of your uterus sheds through your vagina. It's a normal, healthy part of your reproductive cycle.",
            "endometriosis": "Endometriosis is when tissue similar to your uterine lining grows in other places in your body, which can cause pain and heavy periods.",
            "fibroids": "Fibroids are non-cancerous growths in your uterus. They're very common and often don't cause symptoms.",
        }

        term_lower = term.lower().strip()
        if term_lower in term_explanations:
            return term_explanations[term_lower]
        else:
            return f"'{term}' is a medical term related to women's health. I'd recommend asking your healthcare provider for a detailed explanation that's specific to your situation."
