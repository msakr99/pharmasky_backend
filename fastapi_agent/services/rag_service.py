"""
RAG (Retrieval Augmented Generation) Service using ChromaDB
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
import logging
import json
import os
from config import settings
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Global ChromaDB client
_client = None
_collection = None


async def initialize():
    """Initialize ChromaDB and load data"""
    global _client, _collection
    
    if _client is None:
        logger.info("Initializing ChromaDB...")
        
        # Create ChromaDB client
        _client = chromadb.Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.CHROMA_PERSIST_DIR
        ))
        
        # Get or create collection
        _collection = _client.get_or_create_collection(
            name="drugs_catalog",
            metadata={"description": "Pharmaceutical products catalog"}
        )
        
        logger.info(f"ChromaDB initialized. Collection has {_collection.count()} documents")
        
        # Load data if collection is empty
        if _collection.count() == 0:
            await load_data()


async def load_data():
    """Load drug catalog data from exported JSON"""
    global _collection
    
    logger.info("Loading drug catalog into ChromaDB...")
    
    # Path to exported data
    drugs_file = os.path.join(settings.DJANGO_API_URL.replace('http://web:8000', '../'), 'rag_data/drugs.json')
    
    # Alternative: Load from shared volume
    if not os.path.exists(drugs_file):
        drugs_file = '/app/rag_data/drugs.json'
    
    if not os.path.exists(drugs_file):
        logger.warning(f"Drug catalog file not found: {drugs_file}")
        logger.warning("Run 'python manage.py export_rag_data' in Django to generate data")
        return
    
    try:
        with open(drugs_file, 'r', encoding='utf-8') as f:
            drugs = json.load(f)
        
        # Prepare documents for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for drug in drugs:
            # Create searchable text
            doc_text = f"""
اسم الدواء: {drug['name']}
الاسم الإنجليزي: {drug['e_name']}
الشركة: {drug['company']}
الفئة: {drug['category']}
المادة الفعالة: {drug['effective_material']}
السعر: {drug['public_price']} جنيه
الشكل الصيدلي: {drug['shape']}
"""
            
            documents.append(doc_text.strip())
            metadatas.append({
                'id': drug['id'],
                'name': drug['name'],
                'e_name': drug['e_name'],
                'company': drug['company'],
                'price': float(drug['public_price']),
                'category': drug['category']
            })
            ids.append(str(drug['id']))
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            _collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
        
        logger.info(f"✓ Loaded {len(documents)} drugs into ChromaDB")
    
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}", exc_info=True)


async def query(query_text: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Query the RAG database for relevant information
    
    Args:
        query_text: Search query
        top_k: Number of results to return
    
    Returns:
        Dict with 'results' list
    """
    global _collection
    
    if _collection is None:
        await initialize()
    
    try:
        logger.info(f"Querying RAG: '{query_text}' (top_k={top_k})")
        
        # Query ChromaDB
        results = _collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })
        
        logger.info(f"Found {len(formatted_results)} results")
        
        return {
            'success': True,
            'query': query_text,
            'results': formatted_results,
            'count': len(formatted_results)
        }
    
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'query': query_text,
            'results': [],
            'error': str(e)
        }


async def get_drug_info(drug_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific drug
    
    Args:
        drug_name: Drug name to search for
    
    Returns:
        Dict with drug details
    """
    result = await query(drug_name, top_k=1)
    
    if result.get('results'):
        return {
            'success': True,
            'drug': result['results'][0]
        }
    else:
        return {
            'success': False,
            'message': 'Drug not found'
        }

