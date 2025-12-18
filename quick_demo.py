"""
Quick Start Demo for SHL Assessment Recommender
This script demonstrates the system without requiring full data scraping
"""

import json
import os

# Create sample assessment data
sample_assessments = [
    {
        "name": "Java Programming Assessment",
        "url": "https://www.shl.com/solutions/products/java-assessment/",
        "description": "Evaluates Java programming skills including OOP concepts, data structures, and algorithms",
        "test_type": "K",
        "duration_minutes": 60,
        "skills": ["Java", "Programming", "Object-Oriented Design", "Problem Solving"]
    },
    {
        "name": "Communication Skills Assessment",
        "url": "https://www.shl.com/solutions/products/communication-skills/",
        "description": "Measures verbal and written communication abilities",
        "test_type": "P",
        "duration_minutes": 30,
        "skills": ["Communication", "Writing", "Presentation", "Teamwork"]
    },
    {
        "name": "Sales Graduate Assessment",
        "url": "https://www.shl.com/solutions/products/sales-graduate/",
        "description": "Designed for entry-level sales positions",
        "test_type": "P",
        "duration_minutes": 45,
        "skills": ["Sales", "Customer Service", "Persuasion"]
    },
    {
        "name": "Python Developer Assessment",
        "url": "https://www.shl.com/solutions/products/python-assessment/",
        "description": "Tests Python programming, data analysis, and scripting skills",
        "test_type": "K",
        "duration_minutes": 75,
        "skills": ["Python", "Data Analysis", "Programming", "Algorithms"]
    },
    {
        "name": "Leadership Assessment",
        "url": "https://www.shl.com/solutions/products/leadership-skills/",
        "description": "Evaluates leadership capabilities and management potential",
        "test_type": "P",
        "duration_minutes": 40,
        "skills": ["Leadership", "Team Management", "Decision Making", "Strategic Thinking"]
    },
    {
        "name": "SQL Database Assessment",
        "url": "https://www.shl.com/solutions/products/sql-assessment/",
        "description": "Measures SQL query writing and database management skills",
        "test_type": "K",
        "duration_minutes": 50,
        "skills": ["SQL", "Database Management", "Data Querying"]
    },
    {
        "name": "QA Engineer Assessment",
        "url": "https://www.shl.com/solutions/products/qa-testing/",
        "description": "Tests software quality assurance and testing knowledge",
        "test_type": "K",
        "duration_minutes": 60,
        "skills": ["Quality Assurance", "Software Testing", "Test Automation"]
    },
    {
        "name": "Excel Expert Assessment",
        "url": "https://www.shl.com/solutions/products/excel-assessment/",
        "description": "Evaluates advanced Microsoft Excel skills",
        "test_type": "K",
        "duration_minutes": 45,
        "skills": ["Excel", "Data Analysis", "Spreadsheets", "Formulas"]
    },
    {
        "name": "Teamwork Assessment",
        "url": "https://www.shl.com/solutions/products/teamwork-collaboration/",
        "description": "Measures collaboration and team working abilities",
        "test_type": "P",
        "duration_minutes": 35,
        "skills": ["Teamwork", "Collaboration", "Interpersonal Skills"]
    },
    {
        "name": "Data Analyst Assessment",
        "url": "https://www.shl.com/solutions/products/data-analyst/",
        "description": "Tests data analysis, visualization, and statistical skills",
        "test_type": "K",
        "duration_minutes": 70,
        "skills": ["Data Analysis", "Statistics", "Data Visualization", "Python", "SQL"]
    }
]

# Create data directory if it doesn't exist
os.makedirs("data/raw", exist_ok=True)

# Save sample data
output_file = "data/raw/shl_assessments.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(sample_assessments, f, indent=2, ensure_ascii=False)

print(f"✅ Created sample assessment data: {output_file}")
print(f"📊 Total assessments: {len(sample_assessments)}")
print("\nSample assessments created:")
for i, assessment in enumerate(sample_assessments[:5], 1):
    print(f"  {i}. {assessment['name']} ({assessment['test_type']})")

print("\n" + "="*60)
print("Next steps:")
print("="*60)
print("1. Build the vector database:")
print("   python -c \"from src.recommendation.retriever import AssessmentRetriever; r = AssessmentRetriever(); r.create_collection('data/raw/shl_assessments.json')\"")
print("\n2. Start the API server:")
print("   cd src/api && python main.py")
print("\n3. Open frontend:")
print("   cd frontend && python -m http.server 3000")
print("\n4. Or test API directly:")
print("   curl -X POST http://localhost:8000/recommend -H \"Content-Type: application/json\" -d \"{\\\"query\\\": \\\"Java developer\\\"}\"")
