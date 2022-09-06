from datetime import timedelta

import pymongo
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from redis_rate_limiter.exceptions import RateLimitExceeded
from redis_rate_limiter.rate_limiter import RateLimiter

app = FastAPI(title="rate-limiter-example")

client = pymongo.MongoClient()
db = client.get_database("test")


@app.exception_handler(RateLimitExceeded)
async def handle_rate_limit_exceeded(_: Request, exc: RateLimitExceeded):
    return JSONResponse(content=dict(code=1, msg="RateLimitExceeded", success=False))


@app.get("/get")
def get(_id: str):
    return db.example.find_one({"_id": _id})


@app.post("/add")
@RateLimiter(100, period=timedelta(minutes=1))
def add(_id: str):
    print(f"{_id=}")
    return db.example.find_one_and_update(
        {"_id": _id}, {"$inc": {"value": 1}}, return_document=True, upsert=True
    )
