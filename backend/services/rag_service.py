# backend/services/rag_service.py
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

# Try to import OpenAI, but don't fail if not available
try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

logger = logging.getLogger(__name__)


class RAGService:
    """
    Production RAG Service with OpenAI integration and fallback
    """

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
            
            # Try to initialize OpenAI if available
            if OPENAI_AVAILABLE:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key and api_key.strip():
                    try:
                        # Fixed OpenAI client initialization
                        self.client = AsyncOpenAI(
                            api_key=api_key,
                            timeout=30.0  # Remove any other parameters that might cause issues
                        )
                        
                        # Test the client with a simple call
                        test_response = await self.client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": "Hello"}],
                            max_tokens=5
                        )
                        
                        self.use_ai = True
                        logger.info("OpenAI client initialized successfully - using GPT-4o-mini for responses")
                        
                    except Exception as e:
                        logger.warning(f"OpenAI client test failed: {e}")
                        logger.info("Falling back to knowledge-based responses")
                        self.use_ai = False
                else:
                    logger.info("OPENAI_API_KEY not found - using knowledge-based responses")
                    self.use_ai = False
            else:
                logger.info("OpenAI library not available - using knowledge-based responses")
                self.use_ai = False
            
            self.initialized = True
            ai_status = "enabled" if self.use_ai else "disabled"
            logger.info(f"RAG service initialized successfully (AI: {ai_status})")
        
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            # Still mark as initialized so the service can work with fallback responses
            self.use_ai = False
            self.initialized = True
            logger.info("Service will use knowledge-based responses only")

    async def _load_medical_data(self):
        """Load medical Q&A data from JSON file"""
        try:
            # Try multiple possible locations for the dataset
            data_paths = [
                Path("./data/medical_qa_dataset.json"),
                Path("../data/medical_qa_dataset.json"),
                Path("./medical_qa_dataset.json"),
                Path("./backend/data/medical_qa_dataset.json"),
            ]

            dataset_loaded = False
            for data_path in data_paths:
                if data_path.exists():
                    with open(data_path, "r", encoding="utf-8") as f:
                        self.medical_data = json.load(f)
                    logger.info(
                        f"Loaded {len(self.medical_data)} medical Q&A pairs from {data_path}"
                    )
                    dataset_loaded = True
                    break

            if not dataset_loaded:
                logger.warning("Medical dataset not found, creating sample dataset")
                await self._create_sample_dataset()

        except Exception as e:
            logger.error(f"Error loading medical data: {str(e)}")
            await self._create_sample_dataset()

    async def _create_sample_dataset(self):
        """Create sample medical Q&A dataset"""
        self.medical_data = [
            {
                "question": "What is a normal menstrual cycle length?",
                "answer": "A normal menstrual cycle typically ranges from 21 to 35 days, with an average of 28 days. The menstrual period itself usually lasts 3-7 days. Cycles can vary from month to month and may change throughout your life due to factors like stress, weight changes, hormonal fluctuations, or underlying health conditions.",
                "category": "menstruation",
                "tags": ["periods", "cycle", "normal", "duration"],
                "source": "gynecological_guidelines",
            },
            {
                "question": "What are the early signs of pregnancy?",
                "answer": "Early pregnancy signs include missed periods, nausea (morning sickness), breast tenderness and swelling, fatigue, frequent urination, food aversions or cravings, mood changes, light spotting (implantation bleeding), and elevated basal body temperature. However, these symptoms can vary greatly between individuals.",
                "category": "pregnancy",
                "tags": ["pregnancy", "symptoms", "early signs", "conception"],
                "source": "obstetric_care_guidelines",
            },
            {
                "question": "What is PCOS and what are its symptoms?",
                "answer": "PCOS (Polycystic Ovary Syndrome) is a hormonal disorder affecting women of reproductive age. Common symptoms include irregular periods or no periods, excess androgen levels causing acne and hirsutism (excessive hair growth), polycystic ovaries visible on ultrasound, weight gain or difficulty losing weight, insulin resistance, and fertility issues.",
                "category": "pcos",
                "tags": ["PCOS", "hormonal", "symptoms", "ovaries", "androgens"],
                "source": "endocrinology_textbook",
            },
            {
                "question": "What birth control options are available?",
                "answer": "Birth control options include hormonal methods (birth control pills, patches, rings, injections), barrier methods (condoms, diaphragms, cervical caps), intrauterine devices (hormonal and copper IUDs), implants, emergency contraception, and permanent methods. Each has different effectiveness rates, side effects, and considerations.",
                "category": "birth_control",
                "tags": ["contraception", "birth control", "family planning"],
                "source": "contraceptive_guidelines",
            },
            {
                "question": "What should I expect during my first gynecological exam?",
                "answer": "Your first gynecological exam typically includes discussing your medical and sexual history, a physical exam, and possibly a pelvic exam depending on your age and symptoms. The doctor will explain each step, and you can ask questions or request to stop at any time. It's normal to feel nervous.",
                "category": "first_time_sex",
                "tags": ["gynecological exam", "first time", "what to expect"],
                "source": "patient_care_protocols",
            },
            {
                "question": "How can I maintain good vaginal health?",
                "answer": "Maintain vaginal health by practicing good hygiene (gentle washing with water), wearing breathable cotton underwear, avoiding douches and harsh soaps, staying hydrated, eating a balanced diet with probiotics, practicing safe sex, and changing tampons/pads regularly.",
                "category": "vaginal_health",
                "tags": ["hygiene", "vaginal health", "prevention"],
                "source": "gynecological_care_manual",
            },
            {
                "question": "When should I be concerned about irregular periods?",
                "answer": "Consult a healthcare provider if you experience periods lasting longer than 7 days, bleeding between periods, periods occurring more frequently than every 21 days or less frequently than every 35 days, extremely heavy bleeding, severe cramping, or if you haven't had a period for 3+ months.",
                "category": "menstruation",
                "tags": ["irregular periods", "heavy bleeding", "concerning symptoms"],
                "source": "menstrual_disorders_guide",
            },
            {
                "question": "How do I know if I have a yeast infection?",
                "answer": "Yeast infection symptoms include itching and burning in the vaginal area, thick white discharge that looks like cottage cheese, pain during urination or sex, and vulvar swelling. These infections are common and treatable with over-the-counter or prescription antifungal medications.",
                "category": "vaginal_health",
                "tags": ["yeast infection", "symptoms", "treatment"],
                "source": "gynecological_care_manual",
            },
        ]

        # Ensure data directory exists and save the sample data
        try:
            os.makedirs("./data", exist_ok=True)
            with open("./data/medical_qa_dataset.json", "w", encoding="utf-8") as f:
                json.dump(self.medical_data, f, indent=2)
            logger.info(
                f"Created sample medical dataset with {len(self.medical_data)} entries"
            )
        except Exception as e:
            logger.warning(f"Could not save dataset to file: {e}")

    def _find_relevant_context(
        self, question: str, category: Optional[str] = None
    ) -> str:
        """Find relevant medical context for the question"""
        relevant_data = []
        question_lower = question.lower()

        for item in self.medical_data:
            score = 0

            # Category match
            if category and item.get("category") == category:
                score += 0.5

            # Keyword matching
            question_words = question_lower.split()
            item_text = f"{item.get('question', '')} {item.get('answer', '')}".lower()
            item_tags = [tag.lower() for tag in item.get("tags", [])]

            for word in question_words:
                if len(word) > 2:  # Skip short words
                    if word in item_text:
                        score += 0.3
                    if word in item_tags:
                        score += 0.4

            if score > 0:
                relevant_data.append((item, score))

        # Sort by relevance and get top contexts
        relevant_data.sort(key=lambda x: x[1], reverse=True)

        context_parts = []
        for item, score in relevant_data[:3]:  # Top 3 most relevant
            context_parts.append(f"Q: {item['question']}\nA: {item['answer']}")

        return "\n\n".join(context_parts)

    async def get_response(
        self,
        question: str,
        personality_mode: str = "doctor",
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get response for a question"""
        try:
            if self.use_ai and self.client:
                return await self._get_ai_response(question, personality_mode, category)
            else:
                return await self._get_knowledge_based_response(
                    question, personality_mode, category
                )

        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            return self._get_error_response(personality_mode)

    async def _get_ai_response(
        self, question: str, personality_mode: str, category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get AI-powered response using OpenAI"""
        try:
            # Get relevant context from medical data
            context = self._find_relevant_context(question, category)

            # Build personality-specific system prompt
            system_prompts = {
                "doctor": "You are a professional, knowledgeable healthcare assistant specializing in women's health. Provide accurate, clinical information while being compassionate. Always recommend consulting healthcare professionals for serious concerns.",
                "bestie": "You are a caring, supportive best friend who happens to be very knowledgeable about women's health. Use warm, friendly language with appropriate emojis. Be encouraging and supportive while providing accurate information.",
                "sister": "You are a loving, protective older sister who cares deeply about women's health. Use gentle, reassuring language. Be nurturing and understanding while providing helpful, accurate information.",
            }

            system_prompt = system_prompts.get(
                personality_mode, system_prompts["doctor"]
            )

            user_prompt = f"""
Based on the following medical information context, please answer the user's question about women's health:

CONTEXT:
{context}

QUESTION: {question}

Please provide a helpful, accurate response. If the context doesn't contain enough information, use your knowledge but always recommend consulting healthcare professionals for personalized advice.
"""

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            answer = response.choices[0].message.content

            # Create sources from context
            sources = []
            if context:
                sources.append(
                    {
                        "content": "Medical knowledge base and clinical guidelines",
                        "score": 0.9,
                        "metadata": {"source": "ai_enhanced", "model": "gpt-4o-mini"},
                    }
                )

            return {"answer": answer, "sources": sources, "confidence": 0.9}

        except Exception as e:
            logger.error(f"Error with AI response: {str(e)}")
            # Fall back to knowledge-based response
            return await self._get_knowledge_based_response(
                question, personality_mode, category
            )

    async def _get_knowledge_based_response(
        self, question: str, personality_mode: str, category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get response based on medical knowledge base"""
        relevant_data = []
        question_lower = question.lower()

        for item in self.medical_data:
            score = 0

            # Category match
            if category and item.get("category") == category:
                score += 0.5

            # Keyword matching
            question_words = question_lower.split()
            item_question_words = item.get("question", "").lower().split()
            item_answer_words = item.get("answer", "").lower().split()
            item_tags = [tag.lower() for tag in item.get("tags", [])]

            for word in question_words:
                if len(word) > 2:
                    if word in item_question_words:
                        score += 0.3
                    if word in item_answer_words:
                        score += 0.2
                    if word in item_tags:
                        score += 0.4

            if score > 0:
                relevant_data.append({"content": item, "score": min(score, 1.0)})

        if relevant_data:
            relevant_data.sort(key=lambda x: x["score"], reverse=True)
            best_match = relevant_data[0]["content"]
            base_answer = best_match["answer"]

            # Customize based on personality
            response = self._customize_response(base_answer, personality_mode, question)

            sources = [
                {
                    "content": best_match["question"][:100] + "...",
                    "score": relevant_data[0]["score"],
                    "metadata": {
                        "category": best_match.get("category", "general"),
                        "source": "medical_dataset",
                    },
                }
            ]

            return {
                "answer": response,
                "sources": sources,
                "confidence": relevant_data[0]["score"],
            }
        else:
            return self._get_general_response(question, personality_mode)

    def _customize_response(
        self, base_answer: str, personality_mode: str, question: str
    ) -> str:
        """Customize response based on personality mode"""
        if personality_mode == "bestie":
            return f"Hey girl! 💕 {base_answer} Hope this helps! Remember, you know your body best, so don't hesitate to talk to a healthcare provider if you have concerns. You've got this! 🌟"
        elif personality_mode == "sister":
            return f"I'm so glad you asked about this! 🤗 {base_answer} Remember, every woman's experience is different, and it's always okay to seek professional medical advice. Take care of yourself! 💜"
        else:  # doctor mode
            return f"Regarding your question about {question.lower()}: {base_answer} I recommend discussing any specific concerns with your healthcare provider for personalized medical advice."

    def _get_general_response(
        self, question: str, personality_mode: str
    ) -> Dict[str, Any]:
        """Generate general response when no specific data found"""
        responses = {
            "doctor": f"Thank you for your question about '{question}'. While I don't have specific information about this topic in my current knowledge base, I recommend consulting with a qualified healthcare provider for personalized medical advice.",
            "bestie": f"That's a great question about '{question}'! 💕 I don't have specific info about this right now, but I'd definitely suggest chatting with a doctor who can give you the best advice for your situation. You're smart for asking! 🌟",
            "sister": f"I appreciate you asking about '{question}' 🤗 While I don't have detailed information about this specific topic, I encourage you to speak with a healthcare professional who can provide personalized guidance. Never hesitate to advocate for your health! 💜",
        }

        return {
            "answer": responses.get(personality_mode, responses["doctor"]),
            "sources": [],
            "confidence": 0.5,
        }

    def _get_error_response(self, personality_mode: str) -> Dict[str, Any]:
        """Generate error response"""
        responses = {
            "doctor": "I apologize, but I'm experiencing technical difficulties. Please try again or consult with a healthcare provider.",
            "bestie": "Oops! Having a little technical hiccup 😅 Can you try asking again? 💕",
            "sister": "Sorry, having some technical trouble right now 🤗 Please try again! 💜",
        }

        return {
            "answer": responses.get(personality_mode, responses["doctor"]),
            "sources": [],
            "confidence": 0.3,
        }

    async def get_streaming_response(
        self,
        question: str,
        personality_mode: str = "doctor",
        category: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Get streaming response"""
        try:
            response = await self.get_response(question, personality_mode, category)

            # Simulate streaming
            words = response["answer"].split()
            current_chunk = ""

            for i, word in enumerate(words):
                current_chunk += word + " "

                if i % 4 == 3 or i == len(words) - 1:  # Yield every 4 words
                    yield {
                        "chunk": current_chunk,
                        "is_complete": i == len(words) - 1,
                        "sources": response["sources"] if i == len(words) - 1 else [],
                    }
                    current_chunk = ""
                    await asyncio.sleep(0.05)  # Small delay for streaming effect

        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}")
            yield {
                "chunk": "Sorry, I encountered an error processing your request.",
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
                            "content": "You are an expert at explaining medical information in simple, teen-friendly language. Rewrite the given text using everyday words that a teenager would understand. Keep it accurate but make it easy to read.",
                        },
                        {
                            "role": "user",
                            "content": f"Please simplify this medical text for a teenager: {text}",
                        },
                    ],
                    max_tokens=300,
                    temperature=0.5,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Error simplifying with AI: {str(e)}")

        # Fallback to simple text replacement
        simplified = text
        replacements = {
            "syndrome": "condition",
            "hormonal disorder": "hormone problem",
            "reproductive age": "when you can have babies",
            "menstrual cycle": "period cycle",
            "gynecological": "women's health",
            "contraceptives": "birth control",
        }

        for medical_term, simple_term in replacements.items():
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
                            "content": "You are a helpful medical educator. Explain medical terms in simple, clear language that anyone can understand. Focus on women's health topics.",
                        },
                        {
                            "role": "user",
                            "content": f"Please explain the medical term '{term}' in simple language that's easy to understand.",
                        },
                    ],
                    max_tokens=200,
                    temperature=0.5,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Error explaining term with AI: {str(e)}")

        # Fallback explanations
        explanations = {
            "pcos": "PCOS stands for Polycystic Ovary Syndrome. It's a common condition where a woman's hormones are out of balance, causing irregular periods, weight gain, acne, and extra hair growth.",
            "ovulation": "Ovulation is when your ovary releases an egg each month, usually around the middle of your cycle when you're most likely to get pregnant.",
            "menstruation": "Menstruation is your monthly period - when the lining of your uterus sheds. It's a normal part of your reproductive cycle.",
            "hormones": "Hormones are chemical messengers in your body that control many functions, including your menstrual cycle, mood, and growth.",
        }

        term_lower = term.lower().strip()
        if term_lower in explanations:
            return explanations[term_lower]
        else:
            return f"'{term}' is a medical term. I'd recommend asking your healthcare provider for a detailed explanation specific to your situation."
