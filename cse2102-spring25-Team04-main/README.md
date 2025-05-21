# Final-Project
Trello: https://trello.com/b/4rAISfC3/final-group-project

Prototype: https://www.figma.com/design/z1OFMfhYaRgtRM6Zh5Q06q/Team04---Milestone-3?node-id=0-1&t=4bWDDfC1nAzr7Trx-1

## Prerequisites

- Docker
- Git

## Getting Started
### Running the Application

The application is dockerized, so you can build and run it with Docker. We provide two scripts for this purpose:

#### 1. Running the Application (Development Mode)

```bash
# Makes the script executable if needed
chmod +x run_docker.sh

# Run the application
./run_docker.sh
```

This script will:
- Remove any existing database file
- Build the Docker image
- Run the container with the application
- The API will be available at http://localhost:5001
- The Swagger UI will be available at http://localhost:5001/apidocs

#### 2. Running Tests

```bash
# Makes the script executable if needed
chmod +x run_tests.sh

# Run the tests
./run_tests.sh
```

This script will:
- Remove any existing database file (for a clean test environment)
- Build the Docker image
- Run the unit tests inside the Docker container

### Manual Setup (Alternative to Scripts)

If you prefer to run the commands manually:

```bash
# Build the Docker image
docker build -t team04_pet_adoption .

# Run the container
docker run -p 5001:5001 -v "$(pwd):/app" team04_pet_adoption

# Run tests
docker run -v "$(pwd):/app" team04_pet_adoption python -m unittest discover tests
```

## Database Initialization

The database is automatically initialized when the application runs for the first time. The initialization process:

1. Creates the necessary tables according to our ER diagram
2. Populates the tables with initial mock data

The database file (`pet_adoption.db`) is excluded from the repository via `.gitignore` and will be created locally when the application runs.

## API Documentation

The API is documented using Swagger. When the application is running, you can access the Swagger UI at:

```
http://localhost:5001/apidocs
```

This interface allows you to:
- View all available endpoints
- See request/response schemas
- Test the API endpoints in real-time


## 🐾 Pets4Lyfe — Quick Setup Guide
🔹 Backend (Flask)
1. Open Terminal 1
2. Go to the backend folder:
   cd backend
3. Install required packages:
   pip install flask flask-cors werkzeug
4. Run the backend server:
   python app.py


🔹 Frontend (React with Vite)
1. Open Terminal 2
2. Go to the frontend folder:
   cd frontend
3. Install packages:
   npm install
4. Run the frontend:
   npm run dev


Open Your Browser:
- React App: http://localhost:5173
- Backend API: http://localhost:5000


## Project Structure

```
pet4life_api/
├── main.py              # Main application file with routes
├── models/              # Data models
│   ├── __init__.py
│   ├── pet.py           # Pet model
│   ├── user.py          # User model
│   └── application.py   # Adoption application model
├── services/            # Business logic
│   ├── __init__.py
│   ├── pet_service.py   # Pet-related operations
│   ├── user_service.py  # User-related operations
│   └── application_service.py  # Adoption application operations
├── util/                # Utility functions
│   ├── __init__.py
│   ├── db.py            # Database initialization and connection
│   └── mock_data.py     # Mock data for testing
├── tests/               # Unit tests
│   ├── __init__.py
│   ├── test_pet_api.py
│   ├── test_user_api.py
│   └── test_application_api.py
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
├── run_docker.sh        # Script to run the application
└── run_tests.sh         # Script to run tests
```


# Wilson Huang zhh20013
# Vicky Lin vil21004
# Owen Sgro obs18002
# Vincent Kariuki vik22003
