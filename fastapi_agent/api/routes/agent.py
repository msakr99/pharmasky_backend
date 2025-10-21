"""
AI Agent processing endpoints
"""
from fastapi import APIRouter, HTTPException
from api.schemas import AgentRequest, AgentResponse
from services import llm_service, rag_service, mcp_service
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process", response_model=AgentResponse)
async def process_query(request: AgentRequest):
    """
    Process a text query through the AI agent
    
    Steps:
    1. Query RAG for relevant context
    2. Send to LLM for processing
    3. Execute any MCP actions
    4. Return response
    
    POST /agent/process
    Body: {"query": "عايز 10 علب باراسيتامول", "session_id": "..."}
    """
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Step 1: Get context from RAG
        rag_context = await rag_service.query(request.query, top_k=5)
        logger.debug(f"RAG context: {rag_context}")
        
        # Step 2: Build prompt for LLM
        system_prompt = """أنت وكيل مبيعات ذكي لشركة توزيع أدوية.
مهمتك مساعدة الصيادلة في:
- البحث عن الأدوية
- التحقق من المخزون
- إنشاء الطلبات
- الإجابة عن الاستفسارات

استخدم المعلومات التالية للإجابة:
"""
        
        if rag_context.get('results'):
            system_prompt += "\n\nمعلومات الأدوية المتاحة:\n"
            for item in rag_context['results']:
                system_prompt += f"- {item.get('text', '')}\n"
        
        # Step 3: Get LLM response
        llm_response = await llm_service.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query}
            ],
            context=request.context
        )
        
        logger.debug(f"LLM response: {llm_response}")
        
        # Step 4: Extract and execute actions
        actions = []
        
        # Simple intent detection (you can enhance this with better NLP)
        query_lower = request.query.lower()
        
        if any(word in query_lower for word in ['عايز', 'أريد', 'محتاج', 'طلب']):
            # This might be an order request
            logger.info("Detected potential order request")
            # TODO: Extract products and quantities, create order via MCP
        
        if any(word in query_lower for word in ['متوفر', 'موجود', 'فيه']):
            # This might be a stock check
            logger.info("Detected potential stock check")
            # TODO: Extract product name, check stock via MCP
        
        return AgentResponse(
            success=True,
            response=llm_response.get('response', ''),
            actions=actions,
            session_id=request.session_id,
            metadata={
                'rag_results_count': len(rag_context.get('results', [])),
                'intent': 'general'  # TODO: Better intent detection
            }
        )
    
    except Exception as e:
        logger.error(f"Agent processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/rag/query")
async def test_rag_query(q: str, top_k: int = 5):
    """
    Test RAG query directly
    
    GET /agent/rag/query?q=باراسيتامول&top_k=5
    """
    try:
        result = await rag_service.query(q, top_k=top_k)
        return result
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

