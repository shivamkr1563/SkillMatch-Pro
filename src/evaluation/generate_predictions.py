"""
Generate predictions on test set and create submission CSV
"""

import pandas as pd
from pathlib import Path
import sys
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.recommendation.recommender import AssessmentRecommender


def generate_predictions(
    test_data_path: str,
    recommender: AssessmentRecommender,
    output_path: str
):
    """
    Generate predictions for test set and save to CSV
    
    Args:
        test_data_path: Path to test CSV file with queries
        recommender: AssessmentRecommender instance
        output_path: Path to save output CSV
    """
    # Load test queries
    test_df = pd.read_csv(test_data_path)
    
    if 'Query' not in test_df.columns:
        raise ValueError("Test CSV must have a 'Query' column")
    
    queries = test_df['Query'].unique()
    
    print(f"Generating predictions for {len(queries)} test queries...")
    print("="*80)
    
    # Collect all predictions
    all_predictions = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Query: {query[:80]}...")
        
        # Get recommendations
        recommendations = recommender.recommend(query)
        
        print(f"Generated {len(recommendations)} recommendations")
        
        # Add to predictions
        for rec in recommendations:
            all_predictions.append({
                'Query': query,
                'Assessment_url': rec['url']
            })
    
    # Create DataFrame
    predictions_df = pd.DataFrame(all_predictions)
    
    # Save to CSV
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    predictions_df.to_csv(output_file, index=False)
    
    print("\n" + "="*80)
    print("PREDICTION GENERATION COMPLETE")
    print("="*80)
    print(f"Total predictions: {len(predictions_df)}")
    print(f"Unique queries: {len(queries)}")
    print(f"Avg predictions per query: {len(predictions_df) / len(queries):.1f}")
    print(f"\nOutput saved to: {output_file}")
    
    # Show sample
    print("\nSample predictions:")
    print(predictions_df.head(10).to_string(index=False))


def main():
    """Main function"""
    from dotenv import load_dotenv
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate test predictions')
    parser.add_argument('--test', type=str, required=True, help='Path to test CSV')
    parser.add_argument('--output', type=str, default='predictions.csv', help='Output CSV path')
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Initialize recommender
    print("Initializing recommender...")
    recommender = AssessmentRecommender()
    
    # Generate predictions
    generate_predictions(args.test, recommender, args.output)


if __name__ == "__main__":
    main()
