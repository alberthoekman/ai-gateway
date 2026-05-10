# 🚀 AI Gateway - Quickstart Guide

**Get up and running in 2 minutes!**

---

## Option 1: Local Development (No Docker)

### Prerequisites
- Python 3.11+ installed
- Terminal/Command Prompt

### Steps

```bash
# 1. Navigate to project
cd ai-gateway

# 2. Run the start script (automatic setup)
./run.sh
```

**Or manually:**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

### Access the Application
Open your browser: **http://localhost:5000**

---

## Option 2: Docker (Recommended)

### Prerequisites
- Docker installed

### Steps

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Access the Application
Open your browser: **http://localhost:5000**

---

## Testing the POC

### 1. **Test Safe Input** ✅

In the web interface, type:
```
Wat is het weer vandaag in Nederland?
```

Click **"Analyseer Tekst"**

**Expected Result**:
- ✅ Green result box with AI analysis
- 🛡️ Safety Report showing "Geen gevonden" for PII

---

### 2. **Test BSN Detection** 🚫

Type:
```
Mijn BSN nummer is 111222333
```

**Expected Result**:
- ❌ Red "Verzoek Geblokkeerd" message
- 🛡️ Safety Report showing 1 violation (BSN detected)
- Text: "11...33" (masked)

---

### 3. **Test Phone Number Detection** 🚫

Type:
```
Bel me op 0612345678
```

**Expected Result**:
- ❌ Blocked (403)
- Safety Report shows "Telefoonnummer" violation

---

### 4. **Test Multiple Violations** 🚫

Type:
```
BSN: 111222333, telefoon: 0612345678, IBAN: NL91ABNA0417164300
```

**Expected Result**:
- ❌ Blocked
- Safety Report shows 3 violations

---

## API Testing (curl)

### Health Check
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "audit_stats": {
    "total_requests": 5,
    "blocked_requests": 2,
    "avg_processing_time_ms": 42.5
  }
}
```

---

### Analyze Text (Safe)
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Hoe werkt deze AI gateway?"}'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "result": "📊 **Analyse Resultaat (Mock AI)**\n\n• Aantal woorden: 5\n...",
  "safety_report": {
    "scan_performed": true,
    "pii_detected": false,
    "violations_count": 0
  }
}
```

---

### Analyze Text (PII Detected)
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Mijn BSN is 111222333"}'
```

**Response (403 Forbidden):**
```json
{
  "status": "blocked",
  "message": "Persoonlijke gegevens gedetecteerd...",
  "safety_report": {
    "pii_detected": true,
    "violations_count": 1,
    "violations": [
      {
        "type": "BSN (Burgerservicenummer)",
        "masked_value": "11...33",
        "position": 11
      }
    ]
  }
}
```

---

## Running Tests

```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**Expected Output:**
```
tests/test_validator.py::test_valid_bsn_detection PASSED           [ 10%]
tests/test_validator.py::test_invalid_bsn_not_detected PASSED     [ 20%]
tests/test_validator.py::test_phone_number_detection PASSED       [ 30%]
...
===================== 11 passed in 0.15s =====================
```

---

## Troubleshooting

### Port Already in Use
```bash
# Change port in .env or environment variable
export PORT=8080
python app.py
```

### Database Locked Error
```bash
# Remove existing database
rm audit_logs.db
python app.py
```

### Docker Container Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## Next Steps

### 1. **Review the Code**
- `app.py` - Backend logic with audit logging
- `src/validator.py` - PII detection algorithms
- `templates/index.html` - Frontend interface
- `static/js/app.js` - jQuery AJAX logic

### 2. **Explore the Documentation**
- `README.md` - Comprehensive project overview
- `PROJECT_STRUCTURE.md` - Detailed architecture guide
- `Dockerfile` - Container configuration

### 3. **Customize for Production**
- Replace `MockAIService` with real LLM (OpenAI/Claude)
- Add authentication (JWT tokens)
- Set up PostgreSQL for production database
- Configure HTTPS/TLS

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Server port |
| `DEBUG` | `false` | Flask debug mode |
| `STRICT_MODE` | `true` | Enable email/postcode filtering |
| `DATABASE_PATH` | `audit_logs.db` | SQLite database path |

**Example:**
```bash
export STRICT_MODE=false
export PORT=8080
python app.py
```

---

## Monitoring & Statistics

### View Audit Statistics
```bash
curl http://localhost:5000/stats
```

**Response:**
```json
{
  "total_requests": 42,
  "blocked_requests": 7,
  "avg_processing_time_ms": 45.2,
  "total_violations": 12
}
```

### Inspect Database
```bash
sqlite3 data/audit_logs.db

# SQL prompt:
SELECT * FROM request_logs ORDER BY timestamp DESC LIMIT 10;
```

---

## Production Deployment

### Docker Production Build
```bash
# Build optimized image
docker build -t ai-gateway:prod --target production .

# Run with resource limits
docker run -d \
  --name ai-gateway-prod \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  --memory="512m" \
  --cpus="1.0" \
  -e DEBUG=false \
  -e STRICT_MODE=true \
  ai-gateway:prod
```

### Environment Setup
```bash
# Create .env file
cat > .env << EOF
PORT=5000
DEBUG=false
STRICT_MODE=true
DATABASE_PATH=/app/data/audit_logs.db
EOF

# Run with env file
docker run --env-file .env ai-gateway:prod
```

---

## Support & Questions

### Documentation Files
- `README.md` - Main documentation
- `PROJECT_STRUCTURE.md` - Detailed architecture
- `QUICKSTART.md` - This file

### Code Comments
Every function has docstrings explaining:
- Purpose
- Parameters
- Return values
- Example usage

---

## Success Checklist

- [ ] Application starts without errors
- [ ] Web interface loads at http://localhost:5000
- [ ] Safe text returns AI result + green safety report
- [ ] BSN "111222333" is blocked (403)
- [ ] Phone "0612345678" is blocked
- [ ] Health endpoint returns "healthy"
- [ ] Stats endpoint shows request counts
- [ ] Database file created (`audit_logs.db`)
- [ ] Tests pass (`pytest tests/ -v`)

---

**🎉 You're Ready!**

This POC demonstrates:
- ✅ GDPR/AVG compliance (PII filtering)
- ✅ Audit logging for accountability
- ✅ Transparent safety reporting
- ✅ Production-ready architecture (Docker, tests, docs)
- ✅ Clean, maintainable code (PEP8, type hints)

Perfect for a **RIVM AI Programmer** application! 🚀
