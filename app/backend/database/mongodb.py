"""
MongoDB connection and initialization.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from ..config.settings import settings
import certifi


class MongoDB:
    """MongoDB client wrapper."""
    
    client: AsyncIOMotorClient = None
    database = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB."""
        cls.client = AsyncIOMotorClient(
            settings.mongodb_url,
            tlsCAFile=certifi.where()
        )
        cls.database = cls.client[settings.mongodb_database]
        print(f"✓ Connected to MongoDB: {settings.mongodb_database}")
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB."""
        if cls.client:
            cls.client.close()
            print("✓ Disconnected from MongoDB")
    
    @classmethod
    def get_collection(cls, name: str):
        """Get a collection by name."""
        if cls.database is None:
            raise RuntimeError("Database not connected. Call MongoDB.connect() first.")
        return cls.database[name]


# Convenience function
def get_db():
    """Get database instance."""
    return MongoDB.database


