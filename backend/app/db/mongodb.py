from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    client: AsyncIOMotorClient = None
    db_name: str = "steel_db_new"

db = MongoDB()

async def get_database():
    return db.client[db.db_name]

async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient("mongodb://localhost:27017")
        # Validate connection
        await db.client.admin.command('ping')
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")
