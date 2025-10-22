"""
LLM Service using Ollama with Phi-3 Mini
"""
import ollama
import logging
from config import settings
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def chat(messages: List[Dict[str, str]], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Chat with Ollama LLM
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        context: Additional context
    
    Returns:
        Dict with 'response', 'model', etc.
    """
    try:
        logger.info(f"Sending chat request to Ollama ({len(messages)} messages)")
        
        # Call Ollama API
        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages
        )
        
        response_text = response['message']['content']
        
        logger.info(f"LLM response received: '{response_text[:100]}...'")
        
        return {
            'success': True,
            'response': response_text,
            'model': settings.OLLAMA_MODEL,
            'message': response['message']
        }
    
    except Exception as e:
        logger.error(f"LLM error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'response': 'عذراً، حدث خطأ في المعالجة',
            'error': str(e)
        }


async def generate(prompt: str, system: str = None) -> Dict[str, Any]:
    """
    Generate text from a single prompt
    
    Args:
        prompt: User prompt
        system: System prompt
    
    Returns:
        Dict with 'response'
    """
    try:
        logger.info(f"Generating response for prompt: '{prompt[:100]}...'")
        
        response = ollama.generate(
            model=settings.OLLAMA_MODEL,
            prompt=prompt,
            system=system
        )
        
        return {
            'success': True,
            'response': response['response']
        }
    
    except Exception as e:
        logger.error(f"Generation error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'response': 'عذراً، حدث خطأ',
            'error': str(e)
        }


async def extract_intent(text: str) -> Dict[str, Any]:
    """
    Extract intent and entities from user text
    
    This is a simple implementation. For production, consider
    using dedicated NLU services or fine-tuned models.
    
    Args:
        text: User input text
    
    Returns:
        Dict with 'intent', 'entities', 'confidence'
    """
    try:
        system_prompt = """أنت محلل نوايا. حلل النص التالي واستخرج:
1. النية (intent): order, stock_check, search, question, other
2. الكيانات (entities): أسماء الأدوية، الكميات، التفاصيل

أرجع النتيجة بصيغة JSON فقط.
مثال: {"intent": "order", "entities": {"product": "باراسيتامول", "quantity": 10}}
"""
        
        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )
        
        # Try to parse JSON from response
        import json
        try:
            result = json.loads(response['message']['content'])
        except:
            # Fallback to simple intent detection
            text_lower = text.lower()
            if any(word in text_lower for word in ['عايز', 'أريد', 'محتاج', 'طلب']):
                intent = 'order'
            elif any(word in text_lower for word in ['متوفر', 'موجود', 'فيه']):
                intent = 'stock_check'
            elif any(word in text_lower for word in ['ابحث', 'دور', 'find']):
                intent = 'search'
            else:
                intent = 'question'
            
            result = {
                'intent': intent,
                'entities': {},
                'confidence': 0.5
            }
        
        return {
            'success': True,
            **result
        }
    
    except Exception as e:
        logger.error(f"Intent extraction error: {str(e)}")
        return {
            'success': False,
            'intent': 'unknown',
            'entities': {},
            'error': str(e)
        }


async def process_with_functions(text: str, user_id: int = None, session_id: int = None) -> Dict[str, Any]:
    """
    Process text with function calling capabilities
    Similar to ai_agent Django implementation
    """
    try:
        logger.info(f"Processing with functions: {text[:100]}...")
        
        # Get intent and entities
        intent_result = await extract_intent(text)
        intent = intent_result.get('intent', 'unknown')
        entities = intent_result.get('entities', {})
        
        # Process based on intent
        if intent == 'order':
            # Extract product and quantity
            product = entities.get('product', '')
            quantity = entities.get('quantity', 1)
            
            if product:
                # Check availability first
                from services import mcp_service
                availability = await mcp_service.check_availability(product, user_id)
                
                if availability.get('available'):
                    # Create order
                    order_result = await mcp_service.create_order(product, quantity, user_id)
                    return {
                        'success': True,
                        'response': order_result.get('message', 'تم إنشاء الطلب'),
                        'action': 'create_order',
                        'result': order_result
                    }
                else:
                    # Suggest alternatives
                    alt_result = await mcp_service.suggest_alternative(product)
                    return {
                        'success': True,
                        'response': alt_result.get('message', 'المنتج غير متوفر'),
                        'action': 'suggest_alternative',
                        'result': alt_result
                    }
            else:
                return {
                    'success': True,
                    'response': 'من فضلك حدد اسم الدواء المطلوب',
                    'action': 'clarify_product'
                }
        
        elif intent == 'stock_check':
            product = entities.get('product', '')
            if product:
                availability = await mcp_service.check_availability(product, user_id)
                return {
                    'success': True,
                    'response': availability.get('message', 'نتيجة فحص التوفر'),
                    'action': 'check_availability',
                    'result': availability
                }
            else:
                return {
                    'success': True,
                    'response': 'من فضلك حدد اسم الدواء للتحقق من توفره',
                    'action': 'clarify_product'
                }
        
        elif intent == 'search':
            product = entities.get('product', '')
            if product:
                availability = await mcp_service.check_availability(product, user_id)
                return {
                    'success': True,
                    'response': availability.get('message', 'نتائج البحث'),
                    'action': 'search',
                    'result': availability
                }
            else:
                return {
                    'success': True,
                    'response': 'من فضلك حدد اسم الدواء للبحث عنه',
                    'action': 'clarify_product'
                }
        
        else:
            # General question - use RAG + LLM
            from services import rag_service
            rag_context = await rag_service.query(text, top_k=3)
            
            system_prompt = """أنت محمد صقر، تيلي سيلز في شركة فارماسكاي لتجارة وتوزيع الأدوية.
مهمتك مساعدة الصيادلة في إدارة أعمالهم والاستفادة من أفضل العروض المتاحة.

استخدم المعلومات التالية للإجابة:
"""
            
            if rag_context.get('results'):
                system_prompt += "\n\nمعلومات الأدوية المتاحة:\n"
                for item in rag_context['results']:
                    system_prompt += f"- {item.get('text', '')}\n"
            
            # Get LLM response
            llm_response = await chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ])
            
            return {
                'success': True,
                'response': llm_response.get('response', 'عذراً، لم أتمكن من الإجابة'),
                'action': 'general_response',
                'metadata': {
                    'rag_results_count': len(rag_context.get('results', [])),
                    'intent': intent
                }
            }
    
    except Exception as e:
        logger.error(f"Process with functions error: {str(e)}")
        return {
            'success': False,
            'response': 'عذراً، حدث خطأ في المعالجة',
            'error': str(e)
        }
