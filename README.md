# 🛡️ AI Gateway - Verantwoorde AI voor de Publieke Sector

Een **beveiligde Flask-gebaseerde API gateway** die fungeert als een transparante en auditable brug tussen gebruikers en Large Language Models (LLMs), specifiek ontworpen voor **RIVM** en andere Nederlandse overheidsinstanties.

---

## 🎯 Projectdoelen

Deze Proof of Concept (POC) demonstreert hoe **Verantwoorde AI** (Responsible AI) kan worden geïmplementeerd binnen een overheidscontext, met speciale aandacht voor:

1. **Privacy & AVG/GDPR Compliance**: Automatische detectie en blokkering van persoonlijke gegevens (BSN, telefoonnummers, IBAN, postcodes, e-mails) voordat deze een LLM bereiken.
2. **Auditability**: Alle verzoeken worden gelogd in een SQLite-database voor compliance-audits en incident-analyse.
3. **Transparantie**: Elke API-response bevat een "Safety Report" die laat zien welke privacy-controles zijn uitgevoerd.
4. **Betrouwbaarheid**: Gestructureerde error handling, type hinting, en PEP8-conforme code.
5. **Containerization**: Production-ready Dockerfile voor snelle deployment.

---

## 🏗️ Architectuur

```
┌─────────────┐
│   Frontend  │  (HTML/jQuery)
│  index.html │
└──────┬──────┘
       │ POST /analyze
       ▼
┌──────────────────────────────────────┐
│         Flask API Gateway            │
│  ┌────────────────────────────────┐  │
│  │  1. PII Validator (validator.py)│  │  ◄── BSN 11-proof test
│  │     - BSN detection             │  │  ◄── Regex voor NL data
│  │     - Phone number scanning     │  │
│  │     - IBAN, email, postcode     │  │
│  └──────────┬─────────────────────┘  │
│             │ if PII: Block (403)    │
│             ▼                         │
│  ┌────────────────────────────────┐  │
│  │  2. AI Service (OpenAI/Mock)   │  │  ◄── Real or simulated
│  │     - OpenAI GPT-3.5/4         │  │      (auto-switches)
│  │     - Or Mock for testing      │  │
│  └──────────┬─────────────────────┘  │
│             ▼                         │
│  ┌────────────────────────────────┐  │
│  │  3. SQLite Audit Logger        │  │  ◄── Timestamp, input length,
│  │     - Request metadata         │  │      PII violations, status
│  │     - Compliance tracking      │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
       │
       ▼
   Response + Safety Report
```

---

## 📁 Project Structuur

```
ai-gateway/
├── app.py                    # Flask backend met audit logging
├── src/
│   └── validator.py          # PII detectie en filtering (BSN, telefoon, IBAN)
├── templates/
│   └── index.html            # Frontend (jQuery, government-style CSS)
├── static/
│   ├── css/
│   │   └── style.css         # Professionele blue/white styling
│   └── js/
│       └── app.js            # jQuery AJAX voor API calls
├── tests/                    # Unit tests (voor toekomstige uitbreiding)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Multi-stage build voor productie
├── .dockerignore             # Docker build optimalisatie
└── README.md                 # Deze file
```

---

## 🔒 Verantwoorde AI Features

### 1. **PII Filtering (Privacy First)**

De `PIIValidator` in `validator.py` detecteert:

| Data Type | Detectie Methode | Actie |
|-----------|------------------|-------|
| **BSN** | Regex + 11-proof validatie | ❌ Blokkeer verzoek (403) |
| **Telefoonnummers** | NL-formats (+31, 06, 0031) | ❌ Blokkeer verzoek |
| **IBAN** | Dutch IBAN pattern (NL...) | ❌ Blokkeer verzoek |
| **Postcodes** | 1234 AB format | ⚠️ Optioneel (strict_mode) |
| **E-mails** | RFC-compliant regex | ⚠️ Optioneel (strict_mode) |

**Voorbeeld:**
```python
validator = PIIValidator(strict_mode=True)
is_safe, detections, sanitized = validator.validate("Mijn BSN is 111222333")
# is_safe = False
# detections = [PIIDetection(type="BSN", value="11...33", position=11)]
```

### 2. **Audit Logging (Accountability)**

Elke request wordt gelogd in `audit_logs.db`:

```sql
CREATE TABLE request_logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    input_length INTEGER,
    pii_detected BOOLEAN,
    violations_count INTEGER,
    status_code INTEGER,
    processing_time_ms REAL,
    client_ip TEXT,
    user_agent TEXT
);
```

**Use cases:**
- Compliance audits (AVG artikel 30: register van verwerkingsactiviteiten)
- Incident analyse (welke verzoeken werden geblokkeerd?)
- Performance monitoring (gemiddelde verwerkingstijd)

### 3. **Transparantie (Trust)**

Elke API response bevat een **Safety Report**:

```json
{
  "status": "success",
  "result": "AI analyse...",
  "safety_report": {
    "scan_performed": true,
    "pii_detected": false,
    "violations_count": 0,
    "compliance_notes": "Gecontroleerd volgens AVG/GDPR richtlijnen",
    "strict_mode": true
  }
}
```

Als PII wordt gedetecteerd:
```json
{
  "status": "blocked",
  "message": "Persoonlijke gegevens gedetecteerd...",
  "safety_report": {
    "violations": [
      {
        "type": "BSN (Burgerservicenummer)",
        "masked_value": "11...33",
        "position": 15
      }
    ]
  }
}
```

---

## 🚀 Quick Start

### Lokaal draaien (zonder Docker)

1. **Clone het project:**
   ```bash
   cd ai-gateway
   ```

2. **Installeer dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **(Optional) Configure OpenAI for real AI:**
   ```bash
   # Copy the example config
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-your-key-here
   
   # Without API key, uses mock AI (perfect for testing!)
   ```
   
   **See [OPENAI_SETUP.md](OPENAI_SETUP.md) for detailed instructions.**

4. **Start de applicatie:**
   ```bash
   python app.py
   ```

5. **Open in browser:**
   ```
   http://localhost:5000
   ```

### Met Docker (Aanbevolen)

1. **Build de image:**
   ```bash
   docker build -t ai-gateway:latest .
   ```

2. **Run de container:**
   ```bash
   docker run -d \
     --name ai-gateway \
     -p 5000:5000 \
     -v $(pwd)/data:/app/data \
     -e STRICT_MODE=true \
     ai-gateway:latest
   ```

3. **Check health:**
   ```bash
   curl http://localhost:5000/health
   ```

---

## 🧪 Testen

### Test PII Detectie

**Positieve test (veilig):**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Wat is het weer vandaag in Nederland?"}'
```

**Negatieve test (BSN detectie):**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Mijn BSN is 111222333"}' 
# Expected: 403 Forbidden met Safety Report
```

**Test telefoonnummer:**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Bel me op 0612345678"}'
# Expected: 403 Forbidden
```

### Unit Tests (Future Work)

```bash
# Installeer pytest
pip install pytest pytest-cov

# Run tests
pytest tests/ --cov=src --cov-report=html
```

---

## 📊 API Endpoints

### `POST /analyze`

**Input:**
```json
{
  "text": "De tekst om te analyseren"
}
```

**Output (Success):**
```json
{
  "status": "success",
  "result": "AI analyse resultaat...",
  "safety_report": { ... },
  "processing_time_ms": 45.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Output (PII Detected):**
```json
{
  "status": "blocked",
  "message": "Persoonlijke gegevens gedetecteerd...",
  "safety_report": {
    "pii_detected": true,
    "violations": [ ... ]
  }
}
```

### `GET /health`

**Output:**
```json
{
  "status": "healthy",
  "database": "connected",
  "audit_stats": {
    "total_requests": 152,
    "blocked_requests": 8,
    "avg_processing_time_ms": 42.5
  }
}
```

### `GET /stats`

**Output:**
```json
{
  "total_requests": 152,
  "blocked_requests": 8,
  "avg_processing_time_ms": 42.5,
  "total_violations": 12
}
```

---

## 🔐 AVG/GDPR Compliance

Deze POC adresseert de volgende GDPR/AVG principes:

| GDPR Principe | Implementatie |
|---------------|---------------|
| **Data Minimization** (Art. 5.1.c) | PII wordt **nooit** naar de AI gestuurd; detectie + blokkering vooraf |
| **Purpose Limitation** (Art. 5.1.b) | Audit logs bevatten alleen metadata (geen content), voor compliance doeleinden |
| **Accuracy** (Art. 5.1.d) | BSN validatie met 11-proof test (geen false positives) |
| **Accountability** (Art. 5.2) | Volledige audit trail in SQLite database |
| **Transparency** (Art. 12) | Safety Reports laten gebruikers zien dat hun data is gecontroleerd |
| **Security** (Art. 32) | Type hinting, error handling, non-root Docker user |

---

## 🎨 Frontend Design

De frontend volgt **Nederlandse overheids-richtlijnen**:

- **Kleuren**: Blauw (#0077C8) en wit (toegankelijkheid)
- **Typografie**: Segoe UI (professioneel, leesbaar)
- **Responsive**: Mobile-first design met CSS Grid
- **Toegankelijkheid**: WCAG 2.1 AA-compliant (contrast ratios, focus states)
- **Interactie**: Real-time character count, loading spinners, status indicators

---

## 🔄 Roadmap / Toekomstige Uitbreidingen

1. **Echte LLM Integratie**:
   - OpenAI GPT-4 API
   - Azure OpenAI (voor on-premises compliance)
   - Claude API (Anthropic)

2. **Geavanceerde PII Detectie**:
   - Named Entity Recognition (NER) met spaCy/Hugging Face
   - Contextual PII (bijv. "mijn moeder heet [NAAM]")

3. **Rate Limiting**:
   - Per-IP throttling met Redis
   - JWT-based authentication

4. **Monitoring**:
   - Prometheus metrics export
   - Grafana dashboards
   - Sentry error tracking

5. **Multi-tenancy**:
   - Per-organisatie API keys
   - Gescheiden audit logs per tenant

6. **DPIA Integration**:
   - Automatische Data Protection Impact Assessment rapportage

---

## 🤝 Waarom deze POC past bij RIVM

1. **Compliance-first**: AVG/GDPR is niet "nice-to-have" maar het **startpunt** van het design
2. **Transparantie**: Safety Reports bieden inzicht in AI-beslissingen (conform RIVM's wetenschappelijke waarden)
3. **Auditability**: Volledige traceerbaarheid van verzoeken (essentieel voor publieke sector)
4. **Production-ready**: Dockerfile, health checks, structured logging → kan vandaag nog gedeployed
5. **Extensible**: Mock AI service kan vervangen worden door GPT-4/Claude zonder architectuurwijzigingen

---

## 📝 Code Kwaliteit

- ✅ **Type hinting** (Python 3.11+): Alle functies hebben typed parameters en return values
- ✅ **PEP8**: Code volgt Python style guide (verified met `flake8`)
- ✅ **Docstrings**: Elke class/functie heeft documentatie
- ✅ **Error handling**: Try-except blocks met specifieke HTTP status codes (400, 403, 500)
- ✅ **Security**: Non-root Docker user, input validation, SQL injection prevention (parameterized queries)
- ✅ **Modulariteit**: Scheiding tussen validator, database manager, en AI service

---

## 📞 Contact & Vragen

Voor vragen over deze POC:
- **Technische details**: Zie code comments in `app.py` en `validator.py`
- **Deployment**: Zie Dockerfile en Docker Compose voorbeelden
- **RIVM-specifieke aanpassingen**: Deze POC is gemakkelijk uit te breiden met org-specifieke requirements

---

## 📄 Licentie

Deze POC is ontwikkeld als onderdeel van een sollicitatieprocedure voor **RIVM - AI Programmer** positie.

---

**Gebouwd met ❤️ voor Verantwoorde AI in de publieke sector**
