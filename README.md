# 🎯 SkillMatch Pro

AI-powered intelligent recommendation system for matching job requirements with relevant assessments using Retrieval-Augmented Generation (RAG).

## 🎯 Project Overview

This system helps hiring managers and recruiters quickly find the most relevant SHL assessments for their roles by:
- Accepting natural language queries or job description text
- Recommending 5-10 most relevant individual test solutions
- Balancing recommendations across technical and behavioral assessments
- Providing accurate, context-aware suggestions

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │ (React/HTML)
│   Web App       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend       │
│   - /health     │
│   - /recommend  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Recommendation  │
│    Engine       │
│ - Embeddings    │
│ - Vector Search │
│ - LLM Reranking │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector DB      │
│  (ChromaDB)     │
│  377+ Tests     │
└─────────────────┘
```

## 📁 Project Structure

```
shl-assessment-recommender/
├── data/
│   ├── raw/                    # Scraped data
│   ├── processed/              # Processed embeddings
│   ├── train/                  # Training data for evaluation
│   └── test/                   # Test queries
├── src/
│   ├── scraper/
│   │   └── shl_scraper.py     # Web scraper
│   ├── recommendation/
│   │   ├── embedder.py        # Embedding generation
│   │   ├── retriever.py       # Vector search
│   │   └── recommender.py     # Main recommendation logic
│   ├── api/
│   │   ├── main.py            # FastAPI app
│   │   └── models.py          # Pydantic models
│   └── evaluation/
│       └── evaluate.py        # Evaluation metrics
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── notebooks/
│   └── experiments.ipynb      # Development experiments
├── tests/
│   └── test_api.py
├── config/
│   └── settings.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── Dockerfile
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Google Gemini API Key (free tier available)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd shl-assessment-recommender
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Data Collection

Scrape SHL product catalog:
```bash
python src/scraper/shl_scraper.py
```

### Running the API

```bash
uvicorn src.api.main:app --reload --port 8000
```

API will be available at: `http://localhost:8000`

### Running the Frontend

```bash
cd frontend
python -m http.server 3000
```

Frontend will be available at: `http://localhost:3000`

## 📡 API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy"
}
```

### Get Recommendations
```
POST /recommend
Content-Type: application/json

{
  "query": "I am hiring for Java developers who can also collaborate effectively"
}
```

Response:
```json
{
  "query": "I am hiring for Java developers...",
  "recommendations": [
    {
      "assessment_name": "Core Java - Entry Level",
      "assessment_url": "https://www.shl.com/solutions/products/product-catalog/view/core-java-entry-level-new/"
    }
  ],
  "count": 5
}
```

## 📊 Evaluation

Run evaluation on training data:
```bash
python src/evaluation/evaluate.py --data data/train/train.csv
```

Generate test predictions:
```bash
python src/evaluation/generate_predictions.py --output predictions.csv
```

## 🎯 Performance Metrics

- **Mean Recall@10**: Measures retrieval accuracy
- **Recommendation Balance**: Ensures mix of technical (K) and behavioral (P) assessments

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python
- **LLM**: Google Gemini Pro
- **Embeddings**: sentence-transformers
- **Vector DB**: ChromaDB
- **Scraping**: BeautifulSoup4, Selenium
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Docker, Cloud platform (e.g., Render, Railway)

## 📝 Development Approach

1. **Data Collection**: Scraped 377+ individual test solutions from SHL catalog
2. **Embedding Generation**: Created semantic embeddings of all assessments
3. **Retrieval System**: Implemented vector similarity search
4. **LLM Reranking**: Used Gemini to rerank and balance results
5. **Evaluation**: Iteratively improved using labeled training data
6. **API Development**: Built RESTful API with proper validation
7. **Frontend**: Created user-friendly interface
8. **Deployment**: Containerized and deployed to cloud

## 🔍 Key Features

- ✅ Handles natural language queries and job descriptions
- ✅ Balances technical and behavioral assessments
- ✅ Filters by duration constraints
- ✅ Semantic understanding of job requirements
- ✅ Fast response times (<2 seconds)
- ✅ Scalable architecture

## 📄 License

This project is for assessment purposes.

## 👥 Author

Created for SHL GenAI Assessment

## 🙏 Acknowledgments

- SHL for the assessment opportunity
- Google for Gemini API
- Open source community for excellent tools
