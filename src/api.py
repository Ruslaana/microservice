from fastapi import FastAPI
from src.utils.helpers import load_news

app = FastAPI()


@app.get("/news")
def get_news():
    return load_news()
