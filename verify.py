from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Verifier:
    def __init__(self):
        # Neo4j connection
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not uri or not username or not password:
            raise ValueError("Missing required environment variables. Please check your .env file.")
        
        print(f"Debug info:")
        print(f"URI type: {type(uri)}")
        print(f"URI value: {uri}")
        print(f"URI length: {len(uri)}")
        print(f"Username: {username}")
        
        try:
            self.driver = GraphDatabase.driver(uri.strip(), auth=(username, password))
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                print("Successfully connected to Neo4j!")
        except Exception as e:
            print(f"Error connecting to Neo4j: {str(e)}")
            raise
    
    def verify_users(self):
        """Verify user data"""
        print("\nVerifying users...")
        with self.driver.session() as session:
            result = session.run("MATCH (u:User) RETURN u.username, u.name ORDER BY u.username")
            users = [(record["u.username"], record["u.name"]) for record in result]
            print(f"Found {len(users)} users:")
            for username, name in users:
                print(f"- {username}: {name}")
    
    def verify_posts(self):
        """Verify post data"""
        print("\nVerifying posts...")
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User)-[:POSTED]->(p:Post)
                RETURN u.username, p.content, p.timestamp
                ORDER BY p.timestamp DESC
            """)
            posts = [(record["u.username"], record["p.content"], record["p.timestamp"]) for record in result]
            print(f"Found {len(posts)} posts:")
            for username, content, timestamp in posts:
                print(f"- {username} posted at {timestamp}: {content[:50]}...")
    
    def verify_follows(self):
        """Verify follow relationships"""
        print("\nVerifying follow relationships...")
        with self.driver.session() as session:
            result = session.run("""
                MATCH (follower:User)-[:FOLLOWS]->(followee:User)
                RETURN follower.username, followee.username
                ORDER BY follower.username, followee.username
            """)
            follows = [(record["follower.username"], record["followee.username"]) for record in result]
            print(f"Found {len(follows)} follow relationships:")
            for follower, followee in follows:
                print(f"- {follower} follows {followee}")
    
    def run_verification(self):
        """Run all verification checks"""
        print("Starting verification of migrated data...")
        self.verify_users()
        self.verify_posts()
        self.verify_follows()
        print("\nVerification completed!")
    
    def close(self):
        """Close the database connection"""
        self.driver.close()

if __name__ == "__main__":
    verifier = Verifier()
    try:
        verifier.run_verification()
    finally:
        verifier.close() 