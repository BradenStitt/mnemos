import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid
from api import deps
from api.config import settings
from api.util import prepare_results, dedup_combined_results
from fastapi.middleware.cors import CORSMiddleware


pinecone_indexes = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    pinecone_indexes["dense"] = deps.get_pinecone_dense_index()
    pinecone_indexes["sparse"] = deps.get_pinecone_sparse_index()

    yield

    await pinecone_indexes["dense"].close()
    await pinecone_indexes["sparse"].close()

app = FastAPI(lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for memory storage
class MemoryStoreRequest(BaseModel):
    message: str
    timestamp: str
    source: str = "extension"

@app.get("/api/semantic-search")
async def semantic_search(text_query: str = None):
    if not text_query or not text_query.strip():
        raise HTTPException(status_code=422, detail="Text query cannot be empty")
    
    dense_response = await query_dense_index(text_query)
    results = prepare_results(dense_response.result.hits)

    return {"results": results}

@app.get("/api/lexical-search")
async def lexical_search(text_query: str = None):
    if not text_query or not text_query.strip():
        raise HTTPException(status_code=422, detail="Text query cannot be empty")
    
    sparse_response = await query_sparse_index(text_query)
    results = prepare_results(sparse_response.result.hits)
    
    return {"results": results}

@app.get("/api/cascading-retrieval")
async def cascading_retrieval(text_query: str = None):
    if not text_query or not text_query.strip():
        raise HTTPException(status_code=422, detail="Text query cannot be empty")
    
    # Use Pinecone for retrieval
    dense_response, sparse_response = await asyncio.gather(
        query_dense_index(text_query, rerank=True),
        query_sparse_index(text_query, rerank=True)
    )

    combined_results = dense_response.result.hits + sparse_response.result.hits
    deduped_results = dedup_combined_results(combined_results)

    results = deduped_results[:settings.pinecone_top_k]

    return {"results": results}

@app.post("/api/store-memory")
async def store_memory(memory_request: MemoryStoreRequest):
    """Store a new memory in Pinecone"""
    try:
        # Generate a unique ID for the memory
        memory_id = str(uuid.uuid4())
        
        # Create the record for Pinecone upsert
        # Pinecone will automatically generate embeddings using the configured model
        record = {
            "_id": memory_id,
            "chunk_text": memory_request.message,
            "category": "memory"
        }
        
        # Upsert to Pinecone dense index using upsert_records
        # This will automatically generate embeddings using the configured model
        await pinecone_indexes["dense"].upsert_records(
            namespace=settings.pinecone_namespace,
            records=[record]
        )
        
        # Also upsert to sparse inex if you have one configured
        await pinecone_indexes["sparse"].upsert_records(
            namespace=settings.pinecone_namespace,
            records=[record]
        )
        
        print(f"Stored memory in Pinecone: {memory_request.message[:50]}...")
        
        return {
            "success": True,
            "message": "Memory stored successfully in Pinecone",
            "memory_id": memory_id,
            "timestamp": memory_request.timestamp,
            "source": memory_request.source
        }
    except Exception as e:
        print(f"Error storing memory in Pinecone: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store memory: {str(e)}")

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify the service is running"""
    return {
        "status": "ok",
        "message": "Memory service is running with Pinecone",
        "pinecone_connected": True
    }

@app.get("/api/memories")
async def list_memories():
    """List all stored memories (for debugging)"""
    try:
        # Query for all memories
        response = await pinecone_indexes["dense"].search_records(
            namespace=settings.pinecone_namespace,
            query={
                "inputs": {
                    "text": "memory"  # Search for anything to get all memories
                },
                "top_k": 100,  # Get up to 100 memories
                "filter": {
                    "category": "memory"
                }
            }
        )
        
        memories = []
        for hit in response.result.hits:
            memories.append({
                "id": hit._id,
                "text": hit.fields.get("chunk_text", ""),
                "score": hit._score,
                "category": hit.fields.get("category", ""),
                "metadata": hit.metadata
            })
        
        return {
            "count": len(memories),
            "memories": memories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list memories: {str(e)}")
        
async def query_dense_index(text_query: str, rerank: bool = False):
            return await pinecone_indexes['dense'].search_records(
            namespace=settings.pinecone_namespace,
            query={
                "inputs": {
                    "text": text_query,
                },
                "top_k": settings.pinecone_top_k,
                "filter": {
                    "category": "memory"  # Only search for memories stored by the extension
                }
            },
        rerank={
            "model": "cohere-rerank-3.5",
            "rank_fields": ["chunk_text"]
        } if rerank else None
    )

async def query_sparse_index(text_query: str, rerank: bool = False):
            return await pinecone_indexes['sparse'].search_records(
            namespace=settings.pinecone_namespace,
            query={
                "inputs":{
                    "text": text_query,
                },
                "top_k": settings.pinecone_top_k,
                "filter": {
                    "category": "memory"  # Only search for memories stored by the extension
                }
            },
        rerank={
            "model": "cohere-rerank-3.5",
            "rank_fields": ["chunk_text"]
        } if rerank else None
    )