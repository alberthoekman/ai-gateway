# 🤖 OpenAI Integration Setup Guide

This guide shows you how to enable **real AI analysis** using OpenAI's API instead of the mock service.

---

## 🎯 Quick Start (3 Steps)

### 1. Get an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/signup)
2. Sign up or log in
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-...`)

**Important:** OpenAI gives **$5 in free credits** for new accounts, which is plenty for testing!

---

### 2. Configure the API Key

**Option A: Using .env file (Recommended)**

```bash
cd ai-gateway

# Copy the example file
cp .env.example .env

# Edit .env and add your key
nano .env  # or use your favorite editor
```

In `.env`, set:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
AI_MODEL=gpt-3.5-turbo
```

**Option B: Using environment variable**

```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
export AI_MODEL="gpt-3.5-turbo"
```

---

### 3. Install the OpenAI Package

```bash
# Activate your virtual environment
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install/update dependencies
pip install -r requirements.txt
```

---

## 🚀 Test It

```bash
# Start the application
python app.py

# You should see:
# ✅ OpenAI API initialized with model: gpt-3.5-turbo
```

Now test with a real query:

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Wat zijn de belangrijkste gezondheidsrisicos van luchtvervuiling?"}'
```

You should get a real AI-generated response! 🎉

---

## 💰 Cost Management

### Free Tier
- **$5 free credits** for new accounts
- **gpt-3.5-turbo** costs ~$0.002 per request (2000 requests per dollar!)
- Your free credits = ~2,500 test requests

### Model Options

| Model | Cost per 1K tokens | Speed | Quality |
|-------|-------------------|-------|---------|
| **gpt-3.5-turbo** | $0.0015 | ⚡ Fast | ⭐⭐⭐ Good |
| gpt-4 | $0.03 | 🐢 Slower | ⭐⭐⭐⭐⭐ Excellent |
| gpt-4-turbo | $0.01 | ⚡ Fast | ⭐⭐⭐⭐⭐ Excellent |

**Recommendation:** Use `gpt-3.5-turbo` for testing (included by default).

---

## 🔧 Configuration Options

### Environment Variables

```bash
# Required for OpenAI
OPENAI_API_KEY=sk-...

# Optional (with defaults)
AI_MODEL=gpt-3.5-turbo          # Which model to use
PORT=5000                        # Server port
DEBUG=false                      # Debug mode
STRICT_MODE=true                 # PII filtering strictness
DATABASE_PATH=data/audit_logs.db # Database location
```

### Change the Model

To use a different model:

```bash
# In .env
AI_MODEL=gpt-4

# Or as environment variable
export AI_MODEL="gpt-4"
python app.py
```

---

## 🧪 Testing with Docker

If using Docker, pass the API key as an environment variable:

```bash
docker run -d \
  --name ai-gateway \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY="sk-your-key-here" \
  -e AI_MODEL="gpt-3.5-turbo" \
  ai-gateway:latest
```

Or use docker-compose:

```yaml
# docker-compose.yml
services:
  ai-gateway:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AI_MODEL=gpt-3.5-turbo
    env_file:
      - .env
```

Then:
```bash
docker-compose up -d
```

---

## 🔍 Verify It's Working

### Check AI Status Endpoint

```bash
curl http://localhost:5000/ai-status
```

**With API key configured:**
```json
{
  "provider": "OpenAI",
  "model": "gpt-3.5-turbo",
  "api_configured": true,
  "status": "active"
}
```

**Without API key (mock mode):**
```json
{
  "provider": "Mock",
  "model": "Mock AI",
  "api_configured": false,
  "status": "mock_mode"
}
```

---

## 🛡️ Security Best Practices

### ✅ DO:
- ✅ Store API keys in `.env` (gitignored)
- ✅ Use environment variables in production
- ✅ Rotate keys regularly
- ✅ Set usage limits in OpenAI dashboard
- ✅ Monitor API usage

### ❌ DON'T:
- ❌ Commit `.env` to Git
- ❌ Hardcode API keys in code
- ❌ Share keys publicly
- ❌ Use production keys for testing

---

## 🚨 Troubleshooting

### "OpenAI package not installed"

```bash
pip install openai
```

### "Authentication error"

Check that your API key is correct:
```bash
echo $OPENAI_API_KEY
# Should output: sk-...
```

### "Rate limit exceeded"

You've hit OpenAI's rate limit. Wait a few seconds and try again, or upgrade your plan.

### "Insufficient quota"

You've used all your free credits. Add payment method in [OpenAI billing](https://platform.openai.com/account/billing).

### Still using mock mode?

Check the startup logs:
```
✅ OpenAI API initialized with model: gpt-3.5-turbo  ← API working
❌ Not set (using mock)  ← No API key found
```

---

## 📊 Monitor API Usage

### OpenAI Dashboard
- Visit [Usage Dashboard](https://platform.openai.com/usage)
- See costs per day/month
- Set spending limits

### App Audit Logs
```bash
# Check how many requests were processed
curl http://localhost:5000/stats

# View database
sqlite3 data/audit_logs.db "SELECT COUNT(*), AVG(processing_time_ms) FROM request_logs WHERE status_code = 200;"
```

---

## 🎓 Example Queries to Try

Once configured, test with these Dutch public health queries:

```bash
# Health advice
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Wat zijn de symptomen van griep?"}'

# Policy question
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Leg uit wat het RIVM doet tijdens een pandemie"}'

# Data analysis
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Wat is het verschil tussen R0 en Re bij epidemieën?"}'
```

All responses will be in Dutch and include token usage statistics!

---

## 🔄 Switching Between Mock and Real AI

**No code changes needed!** The app automatically switches:

- **With API key** → Uses OpenAI
- **Without API key** → Uses mock service

This means you can:
- Develop locally without API costs (mock mode)
- Test with real AI when needed (set API key)
- Deploy to production with real AI (environment variable)

---

## 💡 Production Recommendations

For a real RIVM deployment:

1. **Use Azure OpenAI** instead of OpenAI API
   - Better for government/healthcare (data sovereignty)
   - Deployed in EU data centers
   - Same API, different endpoint

2. **Set up rate limiting**
   - Prevent API abuse
   - Control costs

3. **Monitor token usage**
   - Track costs per request
   - Alert on unusual patterns

4. **Use prompt caching** (if available)
   - Reduce costs for repeated queries
   - Faster responses

---

## 📞 Need Help?

- **OpenAI Docs**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **API Reference**: [platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)
- **Status Page**: [status.openai.com](https://status.openai.com)
- **Support**: [help.openai.com](https://help.openai.com)

---

## ✅ Success Checklist

- [ ] Created OpenAI account
- [ ] Generated API key
- [ ] Copied `.env.example` to `.env`
- [ ] Set `OPENAI_API_KEY` in `.env`
- [ ] Ran `pip install -r requirements.txt`
- [ ] Started app with `python app.py`
- [ ] Saw "✅ OpenAI API initialized" in logs
- [ ] Tested with `/ai-status` endpoint
- [ ] Made test request with real AI response
- [ ] Checked [usage dashboard](https://platform.openai.com/usage)

---

**🎉 You're now using real AI with PII protection!**

The OpenAI integration is fully working while maintaining all GDPR/AVG compliance features:
- ✅ PII is still filtered **before** reaching OpenAI
- ✅ Audit logs still track all requests
- ✅ Safety reports still included in responses
- ✅ Cost-effective with gpt-3.5-turbo
- ✅ Automatic fallback to mock if API fails
