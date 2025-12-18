@echo off
cd /d "c:\Users\shiva\Desktop\shl assignment"
set PYTHONPATH=c:\Users\shiva\Desktop\shl assignment
echo Starting SkillMatch Pro API...
echo API will be available at http://localhost:8000
echo Swagger docs at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
