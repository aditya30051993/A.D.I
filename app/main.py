from fastapi import FastAPI
from .api import pdf

app = FastAPI()

app.include_router(pdf.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
