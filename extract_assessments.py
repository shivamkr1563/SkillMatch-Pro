"""Extract unique assessments from Gen_AI training dataset and build vector database"""
import pandas as pd
import json
import re
from collections import defaultdict

# Read training data
print("Reading training data...")
train_df = pd.read_csv('data/train-set.csv')
print(f"Loaded {len(train_df)} training examples")

# Extract unique assessment URLs
unique_urls = train_df['Assessment_url'].unique()
print(f"Found {len(unique_urls)} unique assessment URLs")

# Create assessment records from URLs
assessments = []
for url in unique_urls:
    # Extract assessment name from URL
    # Example: https://www.shl.com/solutions/products/product-catalog/view/core-java-entry-level-new/
    match = re.search(r'/view/([^/]+)/?$', url)
    if match:
        slug = match.group(1)
        # Convert slug to readable name
        name = slug.replace('-new/', '').replace('-', ' ').title()
        name = name.replace('Shl ', 'SHL ').replace('Sql', 'SQL').replace('Html', 'HTML')
        name = name.replace('Css', 'CSS').replace('Opq', 'OPQ').replace('Qa', 'QA')
        name = name.replace('Seo', 'SEO').replace('Api', 'API')
    else:
        # Fallback: use last part of URL
        name = url.rstrip('/').split('/')[-1].replace('-', ' ').title()
    
    # Determine test type based on name/URL keywords
    name_lower = name.lower()
    url_lower = url.lower()
    
    if any(kw in name_lower or kw in url_lower for kw in ['java', 'python', 'sql', 'programming', 'developer', 'technical', 'selenium', 'html', 'css', 'javascript', 'database', 'excel', 'automata', 'coding', 'testing', 'qa', 'engineer']):
        test_type = 'K'  # Knowledge/Technical
    elif any(kw in name_lower or kw in url_lower for kw in ['leadership', 'personality', 'communication', 'interpersonal', 'opq', 'sales', 'teamwork', 'behavioral', 'soft skills', 'collaboration']):
        test_type = 'P'  # Personality/Behavioral
    elif any(kw in name_lower or kw in url_lower for kw in ['verify', 'reasoning', 'cognitive', 'numerical', 'verbal', 'inductive', 'deductive']):
        test_type = 'C'  # Cognitive
    else:
        test_type = 'K'  # Default to Knowledge
    
    # Extract skills from name
    skills = []
    skill_keywords = {
        'Java': ['java'],
        'Python': ['python'],
        'SQL': ['sql'],
        'JavaScript': ['javascript'],
        'HTML': ['html'],
        'CSS': ['css'],
        'Excel': ['excel'],
        'Selenium': ['selenium'],
        'Testing': ['testing', 'qa', 'quality'],
        'Leadership': ['leadership', 'management'],
        'Communication': ['communication'],
        'Sales': ['sales'],
        'Teamwork': ['teamwork', 'collaboration'],
        'Programming': ['programming', 'developer', 'coding'],
        'Database': ['database'],
        'SEO': ['seo', 'search engine'],
        'Marketing': ['marketing'],
        'Writing': ['writing', 'written'],
        'English': ['english'],
    }
    
    for skill, keywords in skill_keywords.items():
        if any(kw in name_lower or kw in url_lower for kw in keywords):
            skills.append(skill)
    
    if not skills:
        skills = ['General Assessment']
    
    # Create description based on name and type
    if test_type == 'K':
        description = f"Technical assessment evaluating {', '.join(skills[:3])} skills and knowledge"
    elif test_type == 'P':
        description = f"Behavioral assessment measuring {', '.join(skills[:3])} capabilities and soft skills"
    else:
        description = f"Cognitive assessment testing {', '.join(skills[:3])} reasoning abilities"
    
    assessment = {
        'name': name,
        'url': url,
        'description': description,
        'test_type': test_type,
        'duration_minutes': 60,  # Default duration
        'skills': skills
    }
    assessments.append(assessment)

# Save to JSON
output_file = 'data/raw/shl_assessments.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(assessments, f, indent=2, ensure_ascii=False)

print(f"\n✅ Created {len(assessments)} assessment records")
print(f"📁 Saved to: {output_file}")

# Show statistics
test_type_counts = defaultdict(int)
for a in assessments:
    test_type_counts[a['test_type']] += 1

print(f"\nAssessment Types:")
print(f"  Knowledge/Technical (K): {test_type_counts['K']}")
print(f"  Personality/Behavioral (P): {test_type_counts['P']}")
print(f"  Cognitive (C): {test_type_counts['C']}")

print(f"\nSample assessments:")
for i, a in enumerate(assessments[:5], 1):
    print(f"  {i}. {a['name']} ({a['test_type']}) - {len(a['skills'])} skills")
