# AI Gateway - Responsible AI with PII Protection

A secure Flask-based API gateway that acts as a transparent, auditable bridge between users and Large Language Models (LLMs), with built-in PII filtering and GDPR compliance.

## Features

- **PII Detection & Blocking**: Automatically detects and blocks sensitive Dutch data (BSN numbers, phone numbers, IBAN) before they reach the AI
- **Audit Logging**: Every request is logged to SQLite database with metadata for compliance audits
- **OpenAI Integration**: Supports real LLM analysis via OpenAI API with automatic fallback to mock mode for testing
- **Safety Reports**: Each API response includes a transparency report showing what privacy checks were performed
- **Type Safe**: Full Python type hints for better code quality
- **Docker Ready**: Production-ready containerization with health checks
- **Clean Code**: Follows PEP8 standards with comprehensive error handling

## Quick Start

### Installation

1. Clone the repository:
```bash
cd ai-gateway
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application will start at `http://localhost:5000`

### Test It Out

**Safe input (should return AI analysis):**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the weather today?"}'
```

**Blocked input (contains BSN):**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "My BSN is 111222333"}'
```

Expected response: 403 Forbidden with safety report.

## Configuration

Set environment variables to customize behavior:

```bash
# Enable OpenAI (get key from https://platform.openai.com/api-keys)
export OPENAI_API_KEY="sk-your-key-here"
export AI_MODEL="gpt-3.5-turbo"  # default, or use gpt-4

# Application settings
export PORT=5000
export DEBUG=false
export STRICT_MODE=true  # Also filter emails and postal codes
export DATABASE_PATH=data/audit_logs.db
```

## Docker

Build and run with Docker:

```bash
# Build image
docker build -t ai-gateway:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e STRICT_MODE=true \
  ai-gateway:latest

# Or use docker-compose
docker-compose up -d
```

## Database

The application uses SQLite for audit logging with the following schema:

```sql
CREATE TABLE request_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,             -- Request timestamp (ISO 8601)
    input_length INTEGER NOT NULL,       -- Number of characters in input
    pii_detected BOOLEAN NOT NULL,       -- Whether PII was found (0/1)
    violations_count INTEGER NOT NULL,   -- Number of PII violations
    status_code INTEGER NOT NULL,        -- HTTP response code (200/403/500)
    processing_time_ms REAL,             -- Request processing duration
    client_ip TEXT,                      -- User's IP address
    user_agent TEXT                      -- Client browser/app info
)
```

This logging ensures compliance with GDPR Article 30 (record of processing activities) by:
- Tracking all requests for audit purposes
- Recording only metadata (not user input content)
- Enabling security incident investigation
- Providing performance monitoring

Query examples:
```bash
# View all blocked requests
sqlite3 data/audit_logs.db "SELECT * FROM request_logs WHERE pii_detected = 1;"

# Get statistics
sqlite3 data/audit_logs.db "SELECT COUNT(*) as total, SUM(pii_detected) as blocked FROM request_logs;"

# Check API health
curl http://localhost:5000/health
curl http://localhost:5000/stats
```

## How It Works

1. User submits text via POST `/analyze`
2. PII Validator scans for sensitive Dutch data (BSN, phone, IBAN, etc.)
3. If PII found: request blocked (403), safety report returned
4. If clean: text sent to AI service (OpenAI or mock)
5. Response includes AI result + safety report
6. All metadata logged to database for audit trail

## Project Structure

```
ai-gateway/
├── app.py                    # Flask application and database manager
├── src/
│   ├── validator.py          # PII detection logic
│   └── ai_service.py         # OpenAI integration
├── templates/
│   └── index.html            # Web interface
├── static/
│   ├── css/style.css         # Professional styling
│   └── js/app.js             # Frontend logic
├── tests/
│   └── test_validator.py     # Unit tests
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container configuration
└── docker-compose.yml        # Docker Compose setup
```

## Development

Run tests:
```bash
pytest tests/test_validator.py -v
```

Check code quality:
```bash
# Type hints
python3 -m mypy app.py src/

# Style
flake8 app.py src/ tests/
```

## Notes

- Database directory (`data/`) is created automatically on first run
- Without `OPENAI_API_KEY`, the app uses mock AI (perfect for testing)
- Audit logs contain metadata only - no user input content is stored
- All API responses include a transparency report showing what privacy checks were performed
