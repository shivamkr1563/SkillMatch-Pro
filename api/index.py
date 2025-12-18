from src.api.main import app

# Vercel serverless function handler
def handler(request):
    return app(request)
