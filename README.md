# JEV for Dummies

The stupidly simple HTTP API for Jev.

Turn Jev's decision primitives into simple HTTP GET requests.

No SDK.  
No complicated setup.  
No Jev knowledge required.  

Just HTTP GET → Jev → JSON to get started with Jev.

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

## Interactive API Docs & Playground

Explore and test the API directly from your browser:

- **Interactive Playground & Docs**: [http://localhost:8787/docs](http://localhost:8787/docs) (features live URL generation, preset scenarios, and instant execution)

---

## The Public API

All decision endpoints operate via simple HTTP GET requests with query parameters.

### 1. Choice (`/choice`)

Select one option from a comma-separated list of candidate choices:

```bash
curl "http://localhost:8787/choice?input=Win+a+free+brand+new+car!+Click+here+now.&choices=scam,not+scam"
```

Response:

```json
{
  "result": "scam",
  "confidence": 0.96,
  "probabilities": {
    "scam": 0.96,
    "not scam": 0.04
  }
}
```

Another example (sentiment analysis):

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

### 2. Noul (`/noul`)

Evaluate a yes/no proposition as a boolean (`true` or `false`):

```bash
curl "http://localhost:8787/noul?input=Win+a+free+brand+new+car!+Click+here+now.&question=Is+this+a+scam?"
```

Response:

```json
{
  "result": true,
  "confidence": 0.98
}
```

Another example:

```bash
curl "http://localhost:8787/noul?input=This+is+a+normal+message&question=Is+this+spam?"
```

```json
{
  "result": false
}
```

---

### 3. Score (`/score`)

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

### Health Check (`/health`)

Check service availability:

```bash
curl "http://localhost:8787/health"
```

```json
{
  "status": "ok"
}
```

---

## Metadata & Response Guarantees

- **Uniform Responses**: Every decision response contains a top-level `"result"` field.
- **Confidence & Probabilities**: When returned by TypeSafe, `"confidence"` and/or `"probabilities"` are included. If Jev does not return a field, it is never fabricated.
- **Content-Type**: All responses return `Content-Type: application/json`.
- **Clean Errors**: All errors return a standard 4xx/5xx status with:
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
