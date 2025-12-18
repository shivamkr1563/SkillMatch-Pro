"""
Evaluation module for the recommendation system
Calculates Mean Recall@K and other metrics
"""

import pandas as pd
from typing import List, Dict, Set
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.recommendation.recommender import AssessmentRecommender


def calculate_recall_at_k(predicted: List[str], relevant: List[str], k: int) -> float:
    """
    Calculate Recall@K for a single query
    
    Args:
        predicted: List of predicted URLs
        relevant: List of relevant URLs
        k: Number of top predictions to consider
        
    Returns:
        Recall@K score
    """
    if not relevant:
        return 0.0
    
    predicted_k = set(predicted[:k])
    relevant_set = set(relevant)
    
    num_relevant_retrieved = len(predicted_k.intersection(relevant_set))
    recall = num_relevant_retrieved / len(relevant_set)
    
    return recall


def calculate_mean_recall_at_k(results: List[Dict], k: int = 10) -> float:
    """
    Calculate Mean Recall@K across all queries
    
    Args:
        results: List of result dictionaries with 'predicted' and 'relevant' keys
        k: Number of top predictions to consider
        
    Returns:
        Mean Recall@K score
    """
    if not results:
        return 0.0
    
    recall_scores = []
    for result in results:
        recall = calculate_recall_at_k(
            result['predicted'],
            result['relevant'],
            k
        )
        recall_scores.append(recall)
    
    mean_recall = sum(recall_scores) / len(recall_scores)
    return mean_recall


def evaluate_on_dataset(
    train_data_path: str,
    recommender: AssessmentRecommender,
    k: int = 10
) -> Dict:
    """
    Evaluate recommender on labeled dataset
    
    Args:
        train_data_path: Path to training CSV file
        recommender: AssessmentRecommender instance
        k: Number of recommendations to evaluate
        
    Returns:
        Dictionary with evaluation metrics
    """
    # Load training data
    df = pd.read_csv(train_data_path)
    
    # Group by query to get relevant URLs
    query_groups = df.groupby('Query')['Assessment_url'].apply(list).to_dict()
    
    print(f"Evaluating on {len(query_groups)} queries...")
    print("="*80)
    
    results = []
    query_details = []
    
    for query, relevant_urls in query_groups.items():
        print(f"\nQuery: {query}")
        print(f"Ground truth: {len(relevant_urls)} assessments")
        
        # Get predictions
        recommendations = recommender.recommend(query)
        predicted_urls = [r['url'] for r in recommendations]
        
        print(f"Predicted: {len(predicted_urls)} assessments")
        
        # Calculate recall
        recall = calculate_recall_at_k(predicted_urls, relevant_urls, k)
        
        # Count matches
        matches = set(predicted_urls[:k]).intersection(set(relevant_urls))
        print(f"Matches: {len(matches)}/{len(relevant_urls)}")
        print(f"Recall@{k}: {recall:.3f}")
        
        results.append({
            'predicted': predicted_urls,
            'relevant': relevant_urls
        })
        
        query_details.append({
            'query': query,
            'num_relevant': len(relevant_urls),
            'num_predicted': len(predicted_urls),
            'num_matches': len(matches),
            'recall': recall
        })
    
    # Calculate overall metrics
    mean_recall = calculate_mean_recall_at_k(results, k)
    
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)
    print(f"Mean Recall@{k}: {mean_recall:.4f}")
    print(f"Number of queries: {len(query_groups)}")
    
    # Calculate additional metrics
    avg_matches = sum(d['num_matches'] for d in query_details) / len(query_details)
    avg_relevant = sum(d['num_relevant'] for d in query_details) / len(query_details)
    
    print(f"Average matches per query: {avg_matches:.2f}")
    print(f"Average relevant per query: {avg_relevant:.2f}")
    
    return {
        'mean_recall_at_k': mean_recall,
        'k': k,
        'num_queries': len(query_groups),
        'query_details': query_details,
        'avg_matches': avg_matches,
        'avg_relevant': avg_relevant
    }


def print_detailed_results(evaluation_results: Dict):
    """Print detailed results for each query"""
    print("\n" + "="*80)
    print("DETAILED QUERY RESULTS")
    print("="*80)
    
    for detail in evaluation_results['query_details']:
        print(f"\nQuery: {detail['query'][:80]}...")
        print(f"  Relevant: {detail['num_relevant']}")
        print(f"  Predicted: {detail['num_predicted']}")
        print(f"  Matches: {detail['num_matches']}")
        print(f"  Recall: {detail['recall']:.3f}")


def main():
    """Main evaluation function"""
    from dotenv import load_dotenv
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Evaluate SHL Recommender')
    parser.add_argument('--data', type=str, required=True, help='Path to training CSV')
    parser.add_argument('--k', type=int, default=10, help='K for Recall@K')
    parser.add_argument('--detailed', action='store_true', help='Show detailed results')
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Initialize recommender
    print("Initializing recommender...")
    recommender = AssessmentRecommender()
    
    # Run evaluation
    results = evaluate_on_dataset(args.data, recommender, k=args.k)
    
    # Print detailed results if requested
    if args.detailed:
        print_detailed_results(results)
    
    # Save results
    output_path = Path("data/evaluation_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(output_path, 'w') as f:
        # Remove query_details for JSON serialization
        save_results = {k: v for k, v in results.items() if k != 'query_details'}
        json.dump(save_results, f, indent=2)
    
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
