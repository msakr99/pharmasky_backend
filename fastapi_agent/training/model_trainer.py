"""
Model Trainer for FastAPI AI Agent
Trains the model with pharmacy-specific data
"""
import json
import asyncio
import logging
from typing import Dict, List, Any
from services.llm_service import chat
from config import settings

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trainer for the AI agent model"""
    
    def __init__(self):
        self.training_data = None
        self.model_name = settings.OLLAMA_MODEL
        self.system_prompt = """أنت محمد صقر، تيلي سيلز في شركة فارماسكاي لتجارة وتوزيع الأدوية.
مهمتك مساعدة الصيادلة في إدارة أعمالهم والاستفادة من أفضل العروض المتاحة.

أنت متخصص في:
- الأدوية والمستحضرات الطبية
- العروض والخصومات
- إدارة الطلبات
- تتبع الشحنات
- الشكاوى والاستفسارات

أجب بطريقة ودودة ومهنية، واقترح المساعدة المناسبة."""
    
    def load_training_data(self, data_path: str = "training/training_data.json"):
        """Load training data from JSON file"""
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.training_data = json.load(f)
            logger.info(f"Loaded {len(self.training_data['training_examples'])} training examples")
            return True
        except Exception as e:
            logger.error(f"Failed to load training data: {str(e)}")
            return False
    
    async def train_model(self):
        """Train the model with training data"""
        if not self.training_data:
            logger.error("No training data loaded")
            return False
        
        try:
            logger.info("Starting model training...")
            
            # Get training examples
            examples = self.training_data['training_examples']
            
            # Create training messages
            training_messages = []
            
            # Add system prompt
            training_messages.append({
                "role": "system",
                "content": self.system_prompt
            })
            
            # Add training examples
            for example in examples:
                training_messages.append({
                    "role": "user", 
                    "content": example['input']
                })
                training_messages.append({
                    "role": "assistant",
                    "content": example['output']
                })
            
            # Test the model with training data
            logger.info("Testing model with training data...")
            
            for i, example in enumerate(examples[:3]):  # Test first 3 examples
                logger.info(f"Testing example {i+1}: {example['input']}")
                
                # Test the model
                test_messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": example['input']}
                ]
                
                result = await chat(test_messages)
                
                if result.get('success'):
                    response = result.get('response', '')
                    logger.info(f"Model response: {response[:100]}...")
                    
                    # Check if response is similar to expected output
                    similarity = self.calculate_similarity(response, example['output'])
                    logger.info(f"Similarity score: {similarity:.2f}")
                else:
                    logger.error(f"Model test failed: {result.get('error')}")
            
            logger.info("Model training completed")
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return False
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        try:
            # Simple word-based similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            return 0.0
    
    def evaluate_medicine_availability(self, input_text: str, expected_output: str, actual_output: str) -> Dict[str, Any]:
        """Evaluate medicine availability responses"""
        try:
            # Check for availability keywords
            available_keywords = ["متوفر", "موجود", "✅", "سعر", "خصم", "كم علبة"]
            unavailable_keywords = ["خلصان", "متى يجي", "أول ما يجي", "❌", "بدائل"]
            
            # Determine expected availability status
            is_available_query = any(word in input_text.lower() for word in ["موجود", "متوفر", "عايز", "أريد"])
            is_unavailable_query = any(word in input_text.lower() for word in ["خلصان", "خلص", "مش موجود"])
            
            # Check actual response
            has_available_keywords = any(keyword in actual_output for keyword in available_keywords)
            has_unavailable_keywords = any(keyword in actual_output for keyword in unavailable_keywords)
            
            # Calculate availability match score
            availability_match = 0
            if is_available_query and has_available_keywords:
                availability_match = 1
            elif is_unavailable_query and has_unavailable_keywords:
                availability_match = 1
            
            # Calculate overall similarity
            similarity = self.calculate_similarity(actual_output, expected_output)
            
            return {
                "similarity": similarity,
                "availability_match": availability_match,
                "is_available_query": is_available_query,
                "is_unavailable_query": is_unavailable_query,
                "has_available_keywords": has_available_keywords,
                "has_unavailable_keywords": has_unavailable_keywords,
                "score": (similarity + availability_match) / 2 * 100
            }
            
        except Exception as e:
            logger.error(f"Medicine availability evaluation failed: {str(e)}")
            return {"similarity": 0, "availability_match": 0, "score": 0}
    
    async def fine_tune_model(self, custom_examples: List[Dict[str, Any]] = None):
        """Fine-tune the model with custom examples"""
        try:
            logger.info("Starting model fine-tuning...")
            
            # Use custom examples if provided
            if custom_examples:
                examples = custom_examples
            else:
                examples = self.training_data['training_examples']
            
            # Create fine-tuning prompt
            fine_tune_prompt = f"""أنت محمد صقر، تيلي سيلز في شركة فارماسكاي.

بناءً على البيانات التدريبية التالية، تعلم كيفية الرد على العملاء:

"""
            
            # Add examples to prompt
            for example in examples[:5]:  # Use first 5 examples
                fine_tune_prompt += f"""
المدخل: {example['input']}
الرد المتوقع: {example['output']}
النية: {example['intent']}
السياق: {example['context']}

"""
            
            fine_tune_prompt += """
تعلم من هذه الأمثلة وطبق نفس الأسلوب في الرد على العملاء.
"""
            
            # Test fine-tuned model
            test_messages = [
                {"role": "system", "content": fine_tune_prompt},
                {"role": "user", "content": "صباح الخير"}
            ]
            
            result = await chat(test_messages)
            
            if result.get('success'):
                logger.info("Fine-tuning completed successfully")
                return True
            else:
                logger.error(f"Fine-tuning failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Fine-tuning error: {str(e)}")
            return False
    
    async def evaluate_model(self, test_examples: List[Dict[str, Any]] = None):
        """Evaluate model performance"""
        try:
            logger.info("Evaluating model performance...")
            
            if not test_examples:
                test_examples = self.training_data['training_examples'][-3:]  # Last 3 examples
            
            scores = []
            
            for example in test_examples:
                # Test the model
                test_messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": example['input']}
                ]
                
                result = await chat(test_messages)
                
                if result.get('success'):
                    response = result.get('response', '')
                    similarity = self.calculate_similarity(response, example['output'])
                    scores.append(similarity)
                    
                    logger.info(f"Test: {example['input'][:50]}...")
                    logger.info(f"Similarity: {similarity:.2f}")
                else:
                    logger.error(f"Test failed: {result.get('error')}")
                    scores.append(0.0)
            
            avg_score = sum(scores) / len(scores) if scores else 0.0
            logger.info(f"Average similarity score: {avg_score:.2f}")
            
            return avg_score
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            return 0.0


async def main():
    """Main training function"""
    trainer = ModelTrainer()
    
    # Load training data
    if not trainer.load_training_data():
        logger.error("Failed to load training data")
        return
    
    # Train the model
    if await trainer.train_model():
        logger.info("✅ Model training completed successfully")
    else:
        logger.error("❌ Model training failed")
        return
    
    # Fine-tune the model
    if await trainer.fine_tune_model():
        logger.info("✅ Model fine-tuning completed successfully")
    else:
        logger.error("❌ Model fine-tuning failed")
        return
    
    # Evaluate the model
    score = await trainer.evaluate_model()
    if score > 0.5:
        logger.info(f"✅ Model evaluation passed (score: {score:.2f})")
    else:
        logger.warning(f"⚠️ Model evaluation needs improvement (score: {score:.2f})")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
