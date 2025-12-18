"""
Embedder module for generating embeddings of assessment data
"""

import json
from pathlib import Path
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer


class AssessmentEmbedder:
    """Creates embeddings for SHL assessments"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedder
        
        Args:
            model_name: Name of the sentence transformer model
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def create_assessment_text(self, assessment: Dict) -> str:
        """
        Create a comprehensive text representation of an assessment
        
        Args:
            assessment: Assessment dictionary
            
        Returns:
            Text representation for embedding
        """
        parts = []
        
        # Assessment name
        if assessment.get('name'):
            parts.append(f"Assessment: {assessment['name']}")
        
        # Description
        if assessment.get('description'):
            parts.append(f"Description: {assessment['description']}")
        
        # Test type
        if assessment.get('test_type'):
            test_type_map = {
                'K': 'Knowledge and Skills',
                'P': 'Personality and Behavior',
                'C': 'Cognitive Ability'
            }
            test_type_name = test_type_map.get(assessment['test_type'], assessment['test_type'])
            parts.append(f"Type: {test_type_name}")
        
        # Skills measured
        if assessment.get('skills_measured'):
            skills = ', '.join(assessment['skills_measured'])
            parts.append(f"Measures: {skills}")
        
        # Duration
        if assessment.get('duration_minutes'):
            parts.append(f"Duration: {assessment['duration_minutes']} minutes")
        
        # Category
        if assessment.get('category'):
            parts.append(f"Category: {assessment['category']}")
        
        return " | ".join(parts)
    
    def embed_assessments(self, assessments: List[Dict]) -> np.ndarray:
        """
        Create embeddings for a list of assessments
        
        Args:
            assessments: List of assessment dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        print(f"Creating embeddings for {len(assessments)} assessments...")
        
        # Create text representations
        texts = [self.create_assessment_text(a) for a in assessments]
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True
        )
        
        print(f"Created embeddings with shape: {embeddings.shape}")
        return embeddings
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Create embedding for a query
        
        Args:
            query: Query text
            
        Returns:
            Query embedding
        """
        embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )
        return embedding


def main():
    """Test the embedder"""
    # Load assessments
    data_path = Path("data/raw/shl_assessments.json")
    
    if not data_path.exists():
        print(f"Assessment data not found at {data_path}")
        print("Please run the scraper first: python src/scraper/shl_scraper.py")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        assessments = json.load(f)
    
    print(f"Loaded {len(assessments)} assessments")
    
    # Create embedder
    embedder = AssessmentEmbedder()
    
    # Create embeddings
    embeddings = embedder.embed_assessments(assessments)
    
    # Save embeddings
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    np.save(output_dir / "embeddings.npy", embeddings)
    print(f"\nEmbeddings saved to {output_dir / 'embeddings.npy'}")
    
    # Test query embedding
    test_query = "I need a Java developer with good communication skills"
    query_emb = embedder.embed_query(test_query)
    print(f"\nTest query embedding shape: {query_emb.shape}")


if __name__ == "__main__":
    main()
