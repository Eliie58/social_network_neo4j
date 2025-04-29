# Database Migration Project: SQLite → Neo4j

## Objective
Transform the existing SQLite-based social network application to use Neo4j graph database while maintaining all existing functionality.

## Prerequisites
1 Basic understanding of Cypher query language
2. Python 3.8+ installed

## Workflow Setup
1. **Fork the Repository**
   - Click "Fork" at the top-right of the original repository page
   - Clone your forked copy:
     ```bash
     git clone https://github.com/YOUR_USERNAME/social-network.git
     cd social-network
     ```
2. **Create Feature Branch**
   ```bash
   git checkout -b neo4j-migration
   ```

3. **Commit Changes**
   * After completing EACH task below:
   ```bash
   git add .
   git commit -m "Task X: Brief description of changes"
   ```

4. **Push Changes**
   ```bash
   git push origin neo4j-migration
   ```

5. **(Optional) Create Pull Request**
   * From your fork's GitHub page, create PR to original repository when complete
  
## Tasks

### 1. Environment Setup
- [ ] Add Neo4j Python driver to `requirements.txt`:
  ```python
  neo4j>=5.0.0
  ```
- [ ] Install updated dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Database Initialization
* Create a new Neo4j database instance, or use an existing one.
* Note down connection credentials (URI, username, password)
* Replace SQLite initialization with Neo4j constraints:
    ```cql
    CREATE CONSTRAINT unique_user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
    CREATE CONSTRAINT unique_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE;
    ```

### 3. Database Connection
* Modify Database class constructor to connect to Neo4j.

### 4. User Operations Migration
* Update `create_user` to use Cypher.
* Modify `get_user` to fetch from Neo4j.
* Update `get_all_users`.

### 5. Post Operations Migration
* Change create_post.
* Update `get_posts_by_user` to traverse relationships.

### 6. Follow System Migration
* Convert `follow_user` to create relationships.
* Update unfollow_user to delete relationships.
* Modify get_followers and get_following to use relationship queries.

### 7. Feed Generation Update
* Rewrite get_feed using graph traversal.

### 8. Extra Credit
* Create a migration script to:
    1. Read data from SQLite
    2. Convert relational data to graph nodes/relationships
    3. Insert into Neo4j while preserving relationships
