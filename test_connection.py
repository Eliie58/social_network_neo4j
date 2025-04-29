from neo4j import GraphDatabase

# Replace with your actual password
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "hypothesis001"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def test_connection(tx):
    result = tx.run("RETURN 'Connected to Neo4j!' AS message")
    for record in result:
        print(record["message"])

with driver.session() as session:
    session.read_transaction(test_connection)

driver.close()
