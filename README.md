# JEV for Dummies

The stupidly simple HTTP API for Jev.

Turn Jev's decision primitives into simple HTTP GET requests.

No SDK.  
No complicated request bodies.  
No Jev knowledge required.  

Just HTTP → Jev → JSON to get started with Jev

---

## Install

```bash
git clone https://github.com/your-username/jev-for-dummies.git
cd jev-for-dummies
```

## Configure

Create a `.env` file or export your TypeSafe API key:

```env
TYPESAFE_API_KEY=your_api_key_here
```

## Run

### Using Docker (Recommended)

```bash
docker compose up
```

### Or using Python directly

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8787
```

---

## Interactive API Docs

Explore and test the API directly from your browser with built-in Swagger UI:

```
http://localhost:8787/docs
```

---

## The Entire Public API

The entire service consists of three endpoints, all using simple HTTP GET queries:

### 1. Choice

Select one option from a comma-separated list of choices:

```bash
curl "http://localhost:8787/choice?input=Win+a+free+iPhone&choices=spam,not+spam"
```

Response:

```json
{
  "result": "spam",
  "confidence": 0.94,
  "probabilities": {
    "spam": 0.94,
    "not spam": 0.06
  }
}
```

Another example:

```bash
curl "http://localhost:8787/choice?input=I+love+this+product&choices=positive,negative,neutral"
```

```json
{
  "result": "positive",
  "confidence": 0.91,
  "probabilities": {
    "positive": 0.91,
    "negative": 0.02,
    "neutral": 0.07
  }
}
```

---

### 2. Noul

Evaluate a yes/no decision as a boolean:

```bash
curl "http://localhost:8787/noul?input=Win+a+free+iPhone&question=Is+this+spam?"
```

Response:

```json
{
  "result": true
}
```

Another example:

```bash
curl "http://localhost:8787/noul?input=This+is+a+normal+message&question=Is+this+spam?"
```

Response:

```json
{
  "result": false
}
```

---

### 3. Score

Rate content along an integer numeric scale (`min` to `max`):

```bash
curl "http://localhost:8787/score?input=This+user+is+extremely+toxic&question=How+toxic+is+this?&min=0&max=10"
```

Response:

```json
{
  "result": 8,
  "confidence": 0.89
}
```

---

### Health Check

```bash
curl "http://localhost:8787/health"
```

```json
{
  "status": "ok"
}
```

---

## Metadata

When TypeSafe returns confidence or probability distributions, JEV for Dummies includes them in the JSON response. If Jev does not return a field, it is not fabricated.

All successful responses return `200 OK` with `Content-Type: application/json`.

All error responses return standard JSON error objects:

```json
{
  "error": "choices is required"
}
```

---

## Running Tests

Tests mock the upstream TypeSafe API, so no real API key is required:

```bash
pytest -v
```

---

## License

MIT
