# Vault API

A secure data storage API with semantic search capabilities. Encrypts text data while maintaining searchability through OpenAI embeddings.

## Features

- **🔐 AES-256-GCM Encryption** - Secure text storage
- **🔍 Semantic Search** - Find encrypted data using natural language queries
- **🤖 AI-Powered** - OpenAI embeddings for intelligent matching
- **📊 PostgreSQL + pgvector** - Vector similarity search

## API Endpoints

### Health Checks
```http
GET /api/v1/health/          # Basic health check
GET /api/v1/health/ready     # Database connectivity check
```

### Data Management
```http
POST /api/v1/vault/encrypt   # Encrypt and store text
GET /api/v1/vault/decrypt/{id}  # Decrypt stored text
POST /api/v1/vault/search    # Semantic search
```

## Usage Examples

### Encrypt Text
```bash
curl -X POST "http://localhost:8000/api/v1/vault/encrypt" \
  -H "Content-Type: application/json" \
  -d '{"text": "My secret API key for production"}'
```

### Search Text
```bash
curl -X POST "http://localhost:8000/api/v1/vault/search" \
  -H "Content-Type: application/json" \
  -d '{"text": "API credentials", "limit": 5}'
```

### Decrypt Text
```bash
curl "http://localhost:8000/api/v1/vault/decrypt/{item_id}"
```

## Quick Start

1. **Setup Environment**
   ```bash
   make setup  # Creates venv, installs deps, sets up .env
   ```

2. **Start API**
   ```bash
   make start  # Runs on http://localhost:8000
   ```

3. **View API Docs**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Requirements

- Python 3.11+
- PostgreSQL with pgvector extension
- OpenAI API key

---

*Built with FastAPI, SQLAlchemy, and OpenAI* 