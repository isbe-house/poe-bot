
import os
import pymongo
import motor.motor_asyncio

def mongo_client():
    return pymongo.MongoClient(os.environ['MONGO_URL'])

async def mongo_async_client():
    return motor.motor_asyncio.AsyncIOMotorClient(os.environ['MONGO_URL'])