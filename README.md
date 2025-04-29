# Social Network Simulation

A simple social network web application with Flask backend and HTML/CSS frontend, featuring user profiles, posts, following system, and feed generation.

## Features

- 🧑💻 User profiles with avatar generation
- ✍️ Create and view posts
- 👥 Follow/unfollow other users
- 📰 Personalized feed of followed users' posts
- 🔒 Session-based login/logout
- 📱 Responsive UI with modern design
- 🗄️ SQLite database with separate data access layer
- 📡 RESTful API endpoints

## Project Structure
```
social-network/
├── app.py # Main application code
├── requirements.txt # Dependencies
├── social_network.db # Database file (created automatically)
└── templates/ # HTML templates
    ├── index.html # Homepage with all users
    ├── profile.html # User profile page
    └── feed.html # User feed page
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/social-network.git
   cd social-network
   ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application**
    ```bash
    python app.py
    ```
4. **Access in browser**
    ```
    http://localhost:5000
    ```

## Usage
⚙️ How to Use the Environment Each Time:
cd social_network_neo4j
source env/bin/activate

To exit the environment when you're done:
deactivate

### Frontend Access
1. **Homepage** - View all users and login as any user
2. **User Profile**
   * Create posts (when logged in as the user)
   * Follow/unfollow other users
   * View followers/following lists
   * See post history
3. **Feed** - View posts from followed users

### Sample Users
Default users created on first run:

* Alice Smith (@alice)
* Bob Johnson (@bob)
* Charlie Brown (@charlie)