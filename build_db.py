"""Build the vector database from scraped assessments"""
import sys
import json
sys.path.insert(0, 'c:\\Users\\shiva\\Desktop\\shl assignment')

from src.recommendation.retriever import AssessmentRetriever

print("Building vector database...")
print("This may take a few minutes on first run (downloading embedding model)...")

# Load assessments from JSON file
with open('data/raw/shl_assessments.json', 'r', encoding='utf-8') as f:
    assessments = json.load(f)

print(f"Loaded {len(assessments)} assessments")

retriever = AssessmentRetriever()
retriever.create_collection(assessments, force_recreate=True)

print("\n✅ Vector database created successfully!")
print(f"📁 Location: {retriever.persist_directory}")
