# Library Management API

## Description
This is a Flask-based Library Management API that provides endpoints to manage books and members in a library. It includes functionality for authentication, adding, updating, retrieving, and deleting books and members.

## Features
- JWT Authentication for secure access.
- CRUD operations for books and members.
- SQLite database integration.
- RESTful API design.

## Requirements
- Python 3.10
- Flask
- Flask-SQLAlchemy
- PyJWT

## Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
2. Install dependencies::
   ```bash
   pip install -r requirements.txt
3. Initialize the database and run the application:
   ```bash
   python app.py
4. Use an API client like Postman or cURL to interact with the endpoints.
## API Endpoints

### Authentication
- **POST `/login`**: Generate a JWT token.  
  Request:
  ```json
  {
    "username": "rosansen",
    "password": "rosansen7"
  }

## Running Tests

To ensure the API is functioning correctly, use the following command to run the automated test suite:

```bash
pytest test_library_api.py
```
## Repository URL

[Postman Documentation](https://www.postman.com/rosansen/library/collection/t2g61jd/library-api?action=share&creator=20930953)

