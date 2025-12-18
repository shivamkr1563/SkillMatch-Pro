"""
FastAPI application for SHL Assessment Recommendation System
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.api.models import (
    RecommendationRequest,
    RecommendationResponse,
    AssessmentRecommendation,
    HealthResponse
)
from src.recommendation.recommender import AssessmentRecommender

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SHL Assessment Recommender API",
    description="Intelligent recommendation system for SHL assessments",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommender (singleton)
recommender = None


def get_recommender() -> AssessmentRecommender:
    """Get or create recommender instance"""
    global recommender
    if recommender is None:
        print("Initializing recommendation engine...")
        recommender = AssessmentRecommender(
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
            persist_directory=os.getenv('CHROMA_PERSIST_DIR', './data/chroma_db'),
            min_recommendations=5,
            max_recommendations=10
        )
        print("Recommendation engine initialized")
    return recommender


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("Starting SkillMatch Pro API...")
    get_recommender()
    print("API ready to serve requests")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "SkillMatch Pro API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend (POST)"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running
    
    Returns:
        HealthResponse with status
    """
    return HealthResponse(status="healthy")


@app.post("/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
async def recommend_assessments(request: RecommendationRequest):
    """
    Get assessment recommendations based on a job description or query
    
    Args:
        request: RecommendationRequest containing the query
        
    Returns:
        RecommendationResponse with list of recommended assessments
        
    Raises:
        HTTPException: If recommendation fails
    """
    try:
        # Get recommender
        rec = get_recommender()
        
        # Get recommendations
        results = rec.recommend(request.query, use_llm_reranking=True)
        
        # Format response
        recommendations = [
            AssessmentRecommendation(
                assessment_name=r['name'],
                assessment_url=r['url']
            )
            for r in results
        ]
        
        return RecommendationResponse(
            query=request.query,
            recommendations=recommendations,
            count=len(recommendations)
        )
        
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """Get statistics about the assessment database"""
    try:
        rec = get_recommender()
        collection = rec.retriever.collection
        
        if collection:
            count = collection.count()
            return {
                "total_assessments": count,
                "status": "operational"
            }
        else:
            return {
                "total_assessments": 0,
                "status": "not_initialized"
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('API_PORT', 8000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
