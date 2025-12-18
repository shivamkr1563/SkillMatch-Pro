"""Pydantic models for API requests and responses"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request model for assessment recommendations"""
    query: str = Field(
        ...,
        description="Natural language query or job description",
        min_length=10,
        example="I am hiring for Java developers who can also collaborate effectively with my business teams"
    )


class AssessmentRecommendation(BaseModel):
    """Single assessment recommendation"""
    assessment_name: str = Field(..., description="Name of the assessment")
    assessment_url: str = Field(..., description="URL to the assessment page")


class RecommendationResponse(BaseModel):
    """Response model for assessment recommendations"""
    query: str = Field(..., description="The original query")
    recommendations: List[AssessmentRecommendation] = Field(
        ...,
        description="List of recommended assessments",
        min_items=1,
        max_items=10
    )
    count: int = Field(..., description="Number of recommendations returned")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy", description="Service status")
