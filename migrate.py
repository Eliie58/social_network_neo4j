import sqlite3
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Migrator:
    def __init__(self):
        self.sqlite_conn = sqlite3.connect('social_network.db')
        self.sqlite_cursor = self.sqlite_conn.cursor()
        
        # Neo4j connection
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        print(f"Connecting to Neo4j at {uri}")
        self.neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with self.neo4j_driver.session() as session:
            result = session.run("RETURN 1 as test")
            print("Neo4j connection test successful!")
    
    def cleanup_neo4j(self):
        """Remove all existing data from Neo4j"""
        print("Cleaning up existing Neo4j data...")
        with self.neo4j_driver.session() as session:
            session.run("DROP CONSTRAINT unique_username IF EXISTS")
            
            session.run("""
                MATCH (n)
                DETACH DELETE n
            """)
            print("Cleanup completed!")
    
    def migrate_users(self):
        """Migrate users from SQLite to Neo4j"""
        self.sqlite_cursor.execute("SELECT id, username, name FROM users")
        users = self.sqlite_cursor.fetchall()
        
        with self.neo4j_driver.session() as session:
            for user_id, username, name in users:
                session.run("""
                    CREATE (u:User {username: $username, name: $name, sqlite_id: $sqlite_id})
                """, username=username, name=name, sqlite_id=user_id)
    
    def migrate_posts(self):
        """Migrate posts from SQLite to Neo4j"""
        self.sqlite_cursor.execute("""
            SELECT p.id, p.content, p.timestamp, p.user_id 
            FROM posts p
        """)
        posts = self.sqlite_cursor.fetchall()
        
        with self.neo4j_driver.session() as session:
            for post_id, content, timestamp, user_id in posts:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                iso_timestamp = dt.isoformat()
                
                session.run("""
                    MATCH (u:User {sqlite_id: $user_id})
                    CREATE (p:Post {content: $content, timestamp: datetime($timestamp), sqlite_id: $post_id})
                    CREATE (u)-[:POSTED]->(p)
                """, user_id=user_id, content=content, timestamp=iso_timestamp, post_id=post_id)
    
    def migrate_follows(self):
        """Migrate follow relationships from SQLite to Neo4j"""
        self.sqlite_cursor.execute("""
            SELECT follower_id, followee_id 
            FROM followers
        """)
        follows = self.sqlite_cursor.fetchall()
        
        with self.neo4j_driver.session() as session:
            for follower_id, followee_id in follows:
                session.run("""
                    MATCH (follower:User {sqlite_id: $follower_id})
                    MATCH (followee:User {sqlite_id: $followee_id})
                    MERGE (follower)-[:FOLLOWS]->(followee)
                """, follower_id=follower_id, followee_id=followee_id)
    
    def run_migration(self):
        """Run the complete migration process"""
        print("Starting migration from SQLite to Neo4j...")
        
        self.cleanup_neo4j()
        
        with self.neo4j_driver.session() as session:
            session.run("""
                CREATE CONSTRAINT unique_username IF NOT EXISTS 
                FOR (u:User) REQUIRE u.username IS UNIQUE
            """)
        
        print("Migrating users...")
        self.migrate_users()
        
        print("Migrating posts...")
        self.migrate_posts()
        
        print("Migrating follow relationships...")
        self.migrate_follows()
        
        print("Migration completed successfully!")
    
    def close(self):
        """Close all database connections"""
        self.sqlite_conn.close()
        self.neo4j_driver.close()

if __name__ == "__main__":
    migrator = Migrator()
    try:
        migrator.run_migration()
    finally:
        migrator.close() 