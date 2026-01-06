# Syntelligence OS Cloud Backend

This is the cloud backend for Syntelligence OS, providing scalable ASI processing capabilities.

## Features

- FastAPI-based REST API
- WebSocket support for real-time communication
- SQLAlchemy ORM with database support
- OAuth 2.0 authentication
- Cognitive processing engine with ChromaDB memory
- Containerized deployment with Docker
- End-to-end encryption and security

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env` file

3. Run the application:
   ```bash
   python main.py
   ```

Or with Docker:
```bash
docker build -t syntelligence-backend .
docker run -p 8000:8000 syntelligence-backend
```

## API Endpoints

- `POST /token` - Obtain access token
- `POST /users/` - Create new user
- `GET /users/me/` - Get current user info
- `POST /cognitive/process` - Process cognitive data
- `POST /metrics/update` - Update consciousness metrics
- `WebSocket /ws/{client_id}` - Real-time communication

## Security

README.md
