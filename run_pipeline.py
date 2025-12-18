"""Quick script to run the entire pipeline"""

import subprocess
import sys
from pathlib import Path
import time

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Run the complete pipeline"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   SHL Assessment Recommender - Complete Pipeline        ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠ Warning: Virtual environment not activated")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please activate venv first.")
            return
    
    # Step 1: Install dependencies
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Installing dependencies"
    ):
        return
    
    # Step 2: Check for .env file
    if not Path(".env").exists():
        print("\n⚠ .env file not found")
        print("Please create .env file with your GEMINI_API_KEY")
        print("You can copy from .env.example")
        return
    
    # Step 3: Scrape data (skip if already exists)
    data_file = Path("data/raw/shl_assessments.json")
    if not data_file.exists():
        print("\n📥 Assessment data not found. Starting scraping...")
        if not run_command(
            [sys.executable, "src/scraper/shl_scraper.py"],
            "Scraping SHL catalog"
        ):
            print("Scraping failed. You may need to run it manually.")
            print("Command: python src/scraper/shl_scraper.py")
    else:
        print(f"\n✓ Assessment data already exists: {data_file}")
    
    # Step 4: Build vector database
    chroma_dir = Path("data/chroma_db")
    if not chroma_dir.exists() or not list(chroma_dir.iterdir()):
        print("\n🔨 Building vector database...")
        if not run_command(
            [sys.executable, "src/recommendation/retriever.py"],
            "Building vector database"
        ):
            return
    else:
        print(f"\n✓ Vector database already exists: {chroma_dir}")
    
    # Step 5: Test the recommender
    print("\n🧪 Testing recommender...")
    if not run_command(
        [sys.executable, "src/recommendation/recommender.py"],
        "Testing recommendation engine"
    ):
        print("Test failed but continuing...")
    
    # Step 6: Instructions for running API and frontend
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE!")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("\n1. Start the API:")
    print("   cd src/api")
    print("   python main.py")
    print("   (API will run at http://localhost:8000)")
    
    print("\n2. In a new terminal, start the frontend:")
    print("   cd frontend")
    print("   python -m http.server 3000")
    print("   (Frontend will run at http://localhost:3000)")
    
    print("\n3. Run evaluation (optional):")
    print("   python src/evaluation/evaluate.py --data data/train/train.csv")
    
    print("\n4. Generate test predictions:")
    print("   python src/evaluation/generate_predictions.py --test data/test/test.csv --output predictions.csv")
    
    print("\n5. Run tests:")
    print("   pytest tests/test_api.py -v")
    
    print("\n📚 See SETUP_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()
