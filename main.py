from fastapi import FastAPI
from core.config import setup_environment

app = FastAPI()

# Setup environment variables
setup_environment()

# Include the API routes
from api.routes import router
app.include_router(router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
