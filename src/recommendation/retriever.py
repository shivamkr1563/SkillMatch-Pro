"""
Vector retriever using ChromaDB for similarity search
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer


class AssessmentRetriever:
    """Retrieves relevant assessments using vector similarity"""
    
    def __init__(
        self,
        persist_directory: str = "./data/chroma_db",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the retriever
        
        Args:
            persist_directory: Directory to persist ChromaDB
            model_name: Embedding model name
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.model = SentenceTransformer(model_name)
        
        # Collection name
        self.collection_name = "shl_assessments"
        self.collection = None
    
    def create_collection(self, assessments: List[Dict], force_recreate: bool = False):
        """
        Create and populate ChromaDB collection with assessments
        
        Args:
            assessments: List of assessment dictionaries
            force_recreate: Whether to delete existing collection
        """
        # Delete existing collection if needed
        if force_recreate:
            try:
                self.client.delete_collection(self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            except:
                pass
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "SHL Assessment Catalog"}
        )
        
        # Check if already populated
        if self.collection.count() > 0 and not force_recreate:
            print(f"Collection already has {self.collection.count()} items")
            return
        
        print(f"Populating collection with {len(assessments)} assessments...")
        
        # Prepare data for insertion
        documents = []
        metadatas = []
        ids = []
        
        for i, assessment in enumerate(assessments):
            # Create document text
            doc_text = self._create_document_text(assessment)
            documents.append(doc_text)
            
            # Create metadata
            metadata = {
                'name': assessment.get('name', 'Unknown'),
                'url': assessment.get('url', ''),
                'test_type': assessment.get('test_type', ''),
                'duration_minutes': assessment.get('duration_minutes', 0),
                'description': assessment.get('description', '')[:500],  # Limit length
            }
            metadatas.append(metadata)
            
            # Create ID
            ids.append(f"assessment_{i}")
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            self.collection.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids
            )
            
            print(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        print(f"Collection created with {self.collection.count()} assessments")
    
    def _create_document_text(self, assessment: Dict) -> str:
        """Create searchable text from assessment"""
        parts = []
        
        if assessment.get('name'):
            parts.append(assessment['name'])
        
        if assessment.get('description'):
            parts.append(assessment['description'])
        
        if assessment.get('test_type'):
            test_type_map = {
                'K': 'Knowledge and Skills Technical Ability',
                'P': 'Personality Behavior Soft Skills',
                'C': 'Cognitive Ability Reasoning'
            }
            parts.append(test_type_map.get(assessment['test_type'], ''))
        
        if assessment.get('skills_measured'):
            parts.extend(assessment['skills_measured'])
        
        return ' '.join(parts)
    
    def retrieve(
        self,
        query: str,
        n_results: int = 20,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve relevant assessments for a query
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of assessment dictionaries with scores
        """
        if not self.collection:
            self.collection = self.client.get_collection(self.collection_name)
        
        # Query the collection
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_dict
        )
        
        # Format results
        assessments = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                assessment = {
                    'name': results['metadatas'][0][i]['name'],
                    'url': results['metadatas'][0][i]['url'],
                    'test_type': results['metadatas'][0][i]['test_type'],
                    'duration_minutes': results['metadatas'][0][i]['duration_minutes'],
                    'description': results['metadatas'][0][i]['description'],
                    'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                }
                assessments.append(assessment)
        
        return assessments
    
    def load_collection(self):
        """Load existing collection"""
        try:
            self.collection = self.client.get_collection(self.collection_name)
            print(f"Loaded collection with {self.collection.count()} assessments")
        except:
            print("Collection not found. Please create it first.")


def main():
    """Test the retriever"""
    # Load assessments
    data_path = Path("data/raw/shl_assessments.json")
    
    if not data_path.exists():
        print(f"Assessment data not found at {data_path}")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        assessments = json.load(f)
    
    print(f"Loaded {len(assessments)} assessments")
    
    # Create retriever
    retriever = AssessmentRetriever()
    
    # Create collection
    retriever.create_collection(assessments, force_recreate=True)
    
    # Test retrieval
    test_queries = [
        "I need a Java developer with good communication skills",
        "Looking for sales assessment for new graduates",
        "Leadership assessment for senior executives"
    ]
    
    print("\n" + "="*60)
    print("TESTING RETRIEVAL")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        results = retriever.retrieve(query, n_results=5)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['name']}")
            print(f"   Type: {result['test_type']} | Score: {result['score']:.3f}")
            print(f"   URL: {result['url']}")


if __name__ == "__main__":
    main()
