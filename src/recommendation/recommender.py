"""
Main recommendation engine with LLM-powered reranking and balancing
"""

import re
import os
from typing import List, Dict, Optional
import google.generativeai as genai
from .retriever import AssessmentRetriever


class AssessmentRecommender:
    """Main recommendation engine combining retrieval and LLM reranking"""
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        persist_directory: str = "./data/chroma_db",
        min_recommendations: int = 5,
        max_recommendations: int = 10
    ):
        """
        Initialize the recommender
        
        Args:
            gemini_api_key: Google Gemini API key
            persist_directory: ChromaDB directory
            min_recommendations: Minimum number of recommendations
            max_recommendations: Maximum number of recommendations
        """
        self.min_recommendations = min_recommendations
        self.max_recommendations = max_recommendations
        
        # Initialize retriever
        self.retriever = AssessmentRetriever(persist_directory=persist_directory)
        self.retriever.load_collection()
        
        # Initialize Gemini
        api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.llm = genai.GenerativeModel('gemini-pro')
        else:
            print("Warning: No Gemini API key provided. LLM reranking disabled.")
            self.llm = None
    
    def extract_requirements(self, query: str) -> Dict:
        """
        Extract requirements from query using LLM
        
        Args:
            query: User query
            
        Returns:
            Dictionary of extracted requirements
        """
        if not self.llm:
            return {}
        
        prompt = f"""
        Analyze this job query and extract key requirements:
        
        Query: "{query}"
        
        Extract and return in this format:
        - Technical Skills: [list of technical skills]
        - Soft Skills: [list of soft/behavioral skills]
        - Experience Level: [entry/mid/senior/executive]
        - Duration Constraint: [duration in minutes if mentioned]
        - Role Type: [role/position type]
        
        Be concise and specific.
        """
        
        try:
            response = self.llm.generate_content(prompt)
            return {'analysis': response.text}
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return {}
    
    def parse_duration_from_query(self, query: str) -> Optional[int]:
        """Extract duration constraint from query"""
        # Patterns for duration
        patterns = [
            r'(\d+)\s*(?:minute|min)',
            r'(\d+)\s*(?:hour|hr)',
            r'(\d+)-(\d+)\s*(?:minute|min)'
        ]
        
        query_lower = query.lower()
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                if 'hour' in pattern or 'hr' in pattern:
                    return int(match.group(1)) * 60
                elif len(match.groups()) == 2:
                    return (int(match.group(1)) + int(match.group(2))) // 2
                else:
                    return int(match.group(1))
        
        return None
    
    def balance_recommendations(
        self,
        candidates: List[Dict],
        query: str,
        target_count: int
    ) -> List[Dict]:
        """
        Balance recommendations between technical and behavioral assessments
        
        Args:
            candidates: List of candidate assessments
            query: Original query
            target_count: Target number of recommendations
            
        Returns:
            Balanced list of recommendations
        """
        # Separate by test type
        technical = [a for a in candidates if a.get('test_type') == 'K']
        behavioral = [a for a in candidates if a.get('test_type') == 'P']
        cognitive = [a for a in candidates if a.get('test_type') == 'C']
        other = [a for a in candidates if a.get('test_type') not in ['K', 'P', 'C']]
        
        # Determine if query mentions both technical and soft skills
        query_lower = query.lower()
        has_technical = any(word in query_lower for word in [
            'java', 'python', 'sql', 'programming', 'coding', 'technical',
            'developer', 'engineer', 'data', 'software'
        ])
        has_behavioral = any(word in query_lower for word in [
            'communication', 'leadership', 'teamwork', 'collaboration',
            'personality', 'behavioral', 'soft skill', 'culture', 'fit'
        ])
        
        balanced = []
        
        if has_technical and has_behavioral:
            # Mix of both - aim for 60% technical, 30% behavioral, 10% cognitive
            tech_count = int(target_count * 0.6)
            behav_count = int(target_count * 0.3)
            cog_count = target_count - tech_count - behav_count
            
            balanced.extend(technical[:tech_count])
            balanced.extend(behavioral[:behav_count])
            balanced.extend(cognitive[:cog_count])
            
        elif has_technical:
            # Mostly technical - 70% technical, 20% cognitive, 10% behavioral
            tech_count = int(target_count * 0.7)
            cog_count = int(target_count * 0.2)
            behav_count = target_count - tech_count - cog_count
            
            balanced.extend(technical[:tech_count])
            balanced.extend(cognitive[:cog_count])
            balanced.extend(behavioral[:behav_count])
            
        elif has_behavioral:
            # Mostly behavioral - 70% behavioral, 20% cognitive, 10% technical
            behav_count = int(target_count * 0.7)
            cog_count = int(target_count * 0.2)
            tech_count = target_count - behav_count - cog_count
            
            balanced.extend(behavioral[:behav_count])
            balanced.extend(cognitive[:cog_count])
            balanced.extend(technical[:tech_count])
            
        else:
            # No clear indication - balanced mix
            count_per_type = target_count // 3
            balanced.extend(technical[:count_per_type])
            balanced.extend(behavioral[:count_per_type])
            balanced.extend(cognitive[:count_per_type])
        
        # Fill up to target count with top candidates if needed
        if len(balanced) < target_count:
            remaining = target_count - len(balanced)
            for candidate in candidates:
                if candidate not in balanced:
                    balanced.append(candidate)
                    if len(balanced) >= target_count:
                        break
        
        return balanced[:target_count]
    
    def rerank_with_llm(
        self,
        query: str,
        candidates: List[Dict],
        top_k: int
    ) -> List[Dict]:
        """
        Rerank candidates using LLM
        
        Args:
            query: User query
            candidates: List of candidate assessments
            top_k: Number of top results to return
            
        Returns:
            Reranked list of assessments
        """
        if not self.llm or len(candidates) <= top_k:
            return candidates[:top_k]
        
        # Create prompt for reranking
        candidate_list = "\n".join([
            f"{i+1}. {c['name']} (Type: {c.get('test_type', 'N/A')}, Duration: {c.get('duration_minutes', 'N/A')} min)"
            for i, c in enumerate(candidates[:20])  # Limit to top 20 for LLM
        ])
        
        prompt = f"""
        Given this job requirement query:
        "{query}"
        
        Rank these assessments from most to least relevant:
        {candidate_list}
        
        Return ONLY the numbers of the top {top_k} assessments in order of relevance, separated by commas.
        Example: 3,1,7,2,5
        
        Consider:
        1. Direct relevance to skills mentioned
        2. Balance between technical and soft skills if both are needed
        3. Appropriate for the role level
        
        Numbers only, comma-separated:
        """
        
        try:
            response = self.llm.generate_content(prompt)
            ranking_text = response.text.strip()
            
            # Parse ranking
            indices = [int(x.strip()) - 1 for x in ranking_text.split(',') if x.strip().isdigit()]
            
            # Reorder candidates
            reranked = []
            for idx in indices[:top_k]:
                if 0 <= idx < len(candidates):
                    reranked.append(candidates[idx])
            
            # Fill with remaining candidates if needed
            for candidate in candidates:
                if candidate not in reranked and len(reranked) < top_k:
                    reranked.append(candidate)
            
            return reranked[:top_k]
            
        except Exception as e:
            print(f"LLM reranking error: {e}")
            return candidates[:top_k]
    
    def recommend(
        self,
        query: str,
        use_llm_reranking: bool = True
    ) -> List[Dict]:
        """
        Get assessment recommendations for a query
        
        Args:
            query: User query (job description or requirements)
            use_llm_reranking: Whether to use LLM for reranking
            
        Returns:
            List of recommended assessments
        """
        # Extract duration constraint
        duration_limit = self.parse_duration_from_query(query)
        
        # Retrieve candidates (get more for filtering)
        candidates = self.retriever.retrieve(query, n_results=50)
        
        # Filter by duration if specified
        if duration_limit:
            candidates = [
                c for c in candidates
                if c.get('duration_minutes', 0) <= duration_limit or c.get('duration_minutes') == 0
            ]
        
        # Ensure we have enough candidates
        if len(candidates) < self.min_recommendations:
            print(f"Warning: Only {len(candidates)} candidates found")
        
        # Balance recommendations
        target_count = min(self.max_recommendations, max(self.min_recommendations, len(candidates)))
        balanced = self.balance_recommendations(candidates, query, target_count * 2)
        
        # Rerank with LLM if enabled
        if use_llm_reranking and self.llm:
            final_recommendations = self.rerank_with_llm(query, balanced, target_count)
        else:
            final_recommendations = balanced[:target_count]
        
        # Ensure we have between min and max recommendations
        final_count = max(self.min_recommendations, min(self.max_recommendations, len(final_recommendations)))
        
        return final_recommendations[:final_count]


def main():
    """Test the recommender"""
    from pathlib import Path
    import json
    
    # Load API key from .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create recommender
    recommender = AssessmentRecommender()
    
    # Test queries
    test_queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams",
        "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript",
        "I want to hire new graduates for a sales role, test should be about an hour",
        "Content Writer required, expert in English and SEO",
        "Senior Data Analyst with 5 years experience in SQL, Excel and Python, 1-2 hour assessment"
    ]
    
    print("="*80)
    print("TESTING RECOMMENDATION ENGINE")
    print("="*80)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        
        recommendations = recommender.recommend(query)
        
        print(f"\nRecommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['name']}")
            print(f"   Type: {rec.get('test_type', 'N/A')} | "
                  f"Duration: {rec.get('duration_minutes', 'N/A')} min | "
                  f"Score: {rec.get('score', 0):.3f}")
            print(f"   URL: {rec['url']}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    main()
