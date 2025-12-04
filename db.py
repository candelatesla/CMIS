"""
Database module for MongoDB connection and operations
"""
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from config import MONGODB_URI, MONGODB_DB_NAME

# Global database client
_client: MongoClient = None
_db: Database = None


def get_database() -> Database:
    """
    Get the MongoDB database instance
    
    Returns:
        Database: MongoDB database instance
    """
    global _client, _db
    
    if _db is None:
        _client = MongoClient(MONGODB_URI)
        _db = _client[MONGODB_DB_NAME]
        print(f"Connected to MongoDB database: {MONGODB_DB_NAME}")
    
    return _db


def get_collection(name: str) -> Collection:
    """
    Get a MongoDB collection by name
    
    Args:
        name: The name of the collection
        
    Returns:
        Collection: MongoDB collection instance
    """
    db = get_database()
    return db[name]


def close_connection():
    """Close the MongoDB connection"""
    global _client
    if _client is not None:
        _client.close()
        print("MongoDB connection closed")
