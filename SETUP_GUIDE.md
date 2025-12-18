# SHL Assessment Recommender - Setup Guide

## Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Data Collection

Scrape the SHL catalog:
```bash
python src/scraper/shl_scraper.py
```

This will create `data/raw/shl_assessments.json` with 377+ assessments.

### 4. Build Vector Database

```bash
python src/recommendation/retriever.py
```

This creates the ChromaDB vector database in `data/chroma_db/`.

### 5. Run the API

```bash
# From project root
cd src/api
python main.py

# Or using uvicorn directly
uvicorn src.api.main:app --reload --port 8000
```

API will be available at: `http://localhost:8000`

### 6. Run the Frontend

```bash
# Open a new terminal
cd frontend
python -m http.server 3000
```

Frontend will be available at: `http://localhost:3000`

## Testing

### Test API Endpoints

1. Health check:
```bash
curl http://localhost:8000/health
```

2. Get recommendations:
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "I need a Java developer with good communication skills"}'
```

### Run Evaluation

```bash
python src/evaluation/evaluate.py --data data/train/train.csv --k 10 --detailed
```

### Generate Test Predictions

```bash
python src/evaluation/generate_predictions.py --test data/test/test.csv --output predictions.csv
```

## Docker Deployment

### Build Image

```bash
docker build -t shl-recommender .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env shl-recommender
```

## Project Structure

```
.
├── src/
│   ├── scraper/           # Web scraping
│   ├── recommendation/    # Core engine
│   ├── api/              # FastAPI backend
│   └── evaluation/       # Metrics and testing
├── frontend/             # Web interface
├── data/                 # Data storage
├── config/              # Configuration
└── requirements.txt     # Dependencies
```

## Troubleshooting

### "ChromaDB collection not found"
Run: `python src/recommendation/retriever.py`

### "No Gemini API key"
Add your key to `.env` file

### "Cannot connect to API"
Ensure the API is running: `python src/api/main.py`

### "Scraping failed"
Try with `headless=False` in the scraper to see browser

## Next Steps

1. Scrape data ✓
2. Build vector database ✓
3. Run API ✓
4. Test frontend ✓
5. Evaluate on training data
6. Generate test predictions
7. Deploy to cloud
8. Create approach document
9. Submit GitHub repo, API URL, frontend URL, and predictions CSV

## Resources

- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
