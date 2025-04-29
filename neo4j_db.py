from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jDatabase:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with required constraints"""
        with self.driver.session() as session:
            session.run("""
                CREATE CONSTRAINT unique_user_id IF NOT EXISTS 
                FOR (u:User) REQUIRE u.id IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT unique_username IF NOT EXISTS 
                FOR (u:User) REQUIRE u.username IS UNIQUE
            """)
    
    def close(self):
        """Close the database connection"""
        self.driver.close() 