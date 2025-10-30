# 🔬 SNOUTIQ Technical Documentation

**Complete technical overview of the RAG-based veterinary symptom checker system**

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Code Structure](#code-structure)
3. [Core Components Explained](#core-components-explained)
4. [Data Flow](#data-flow)
5. [ML Models Used](#ml-models-used)
6. [Database Structure](#database-structure)
7. [Performance Optimization](#performance-optimization)

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│                    (PHP Frontend)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP POST /query
                        │ JSON Request
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask API Layer                           │
│                     (app.py)                                 │
│  - Request Validation                                        │
│  - Error Handling                                            │
│  - CORS Management                                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG System Core                           │
│                  (rag_system.py)                             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. Query Expansion                                 │    │
│  │     - Medical synonym expansion                     │    │
│  │     - Emergency keyword detection                   │    │
│  └────────────────────────────────────────────────────┘    │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  2. Embedding Generation                            │    │
│  │     - Sentence Transformers                         │    │
│  │     - Model: all-MiniLM-L6-v2                      │    │
│  │     - Output: 384-dim vector                        │    │
│  └────────────────────────────────────────────────────┘    │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  3. Vector Search                                   │    │
│  │     - FAISS IndexFlatIP                            │    │
│  │     - Cosine similarity search                      │    │
│  │     - Top-K retrieval (K=10)                       │    │
│  └────────────────────────────────────────────────────┘    │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  4. Result Ranking                                  │    │
│  │     - Species filtering                             │    │
│  │     - Severity boosting                             │    │
│  │     - Score normalization                           │    │
│  └────────────────────────────────────────────────────┘    │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  5. Context Building                                │    │
│  │     - Top 3 matches                                 │    │
│  │     - Pet medical history                           │    │
│  │     - Emergency flags                               │    │
│  └────────────────────────────────────────────────────┘    │
│                        │                                     │
│                        ▼                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  6. LLM Generation                                  │    │
│  │     - Google Gemini 2.0 Flash                      │    │
│  │     - Structured prompt                             │    │
│  │     - JSON response format                          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Structured JSON Response                    │
│  {                                                           │
│    "pet_name": "...",                                       │
│    "summary": "...",                                        │
│    "immediate_steps": [...],                                │
│    "urgency_level": "...",                                  │
│    ...                                                       │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Code Structure

```
Pet-Symptom-Checker/
├── app.py                      # Flask API application
├── rag_system.py               # Core RAG logic
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version specification
├── Procfile                    # Deployment configuration
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
│
├── datasets/                   # Veterinary knowledge base
│   ├── master_emergency_dataset.json
│   ├── master_digestive_dataset.json
│   ├── master_respiratory_dataset.json
│   ├── master_urinary_dataset.json
│   ├── master_joint_mobility_dataset.json
│   ├── master_reproductive_dataset.json
│   ├── master_skin_coat_dataset.json
│   ├── master_eyes_ears_dataset.json
│   ├── master_behavioral_dataset.json
│   ├── master_nutrition_weight_dataset.json
│   └── master_pet_health_dataset.json
│
├── frontend/                   # Frontend files
│   └── index.php               # Demo frontend interface
│
├── backend/                    # Backend (duplicate for deployment)
│   ├── app.py
│   ├── rag_system.py
│   ├── requirements.txt
│   └── datasets/
│
├── DEPLOYMENT_GUIDE.md         # Deployment instructions
├── TECHNICAL_DOCUMENTATION.md  # This file
├── README.md                   # Project overview
└── SETUP_GUIDE.md             # Quick setup guide
```

---

## 🧩 Core Components Explained

### 1. app.py - Flask API Application

**Purpose**: HTTP API layer that receives requests and returns responses

**Key Functions:**

#### `initialize_rag_system()`
```python
def initialize_rag_system():
    """
    Loads AI models and datasets on server startup
    - Configures Gemini API with key from .env
    - Initializes RAG system
    - Loads all 11 dataset files
    - Creates FAISS vector index
    """
```

**What it does:**
1. Reads `GEMINI_API_KEY` from environment
2. Creates `SnoutiqRAG` instance
3. Finds all `master_*_dataset.json` files
4. Loads and processes datasets
5. Sets global `rag_system` variable

**When it runs**: On server startup (when Gunicorn imports the module)

#### `@app.route('/query', methods=['POST'])`
```python
def process_query():
    """
    Main endpoint for symptom analysis
    1. Validates request data
    2. Extracts pet details
    3. Calls RAG system
    4. Returns JSON response
    """
```

**Request validation:**
- Checks for JSON content-type
- Validates required fields: `name`, `species`, `query`
- Validates species is "Dog" or "Cat"
- Validates query length (10-1000 characters)

**Error handling:**
- 400: Bad request (missing fields, invalid data)
- 503: Service unavailable (RAG not initialized)
- 500: Internal server error

---

### 2. rag_system.py - Core RAG Logic

**Purpose**: Implements the Retrieval-Augmented Generation system

**Key Class: `SnoutiqRAG`**

#### Constructor: `__init__(api_key)`
```python
def __init__(self, api_key: str):
    self.embedder = SentenceTransformer(EMBEDDING_MODEL)
    genai.configure(api_key=api_key)
    self.llm = genai.GenerativeModel(GEMINI_MODEL)
    self.documents = []      # List of text entries
    self.metadata = []       # List of metadata dicts
    self.index = None        # FAISS index
    self.loaded = False      # Initialization flag
```

**Models loaded:**
- `all-MiniLM-L6-v2`: 384-dimensional sentence embeddings
- `gemini-2.0-flash`: Google's fast LLM for generation

#### Method: `load_datasets(dataset_files)`
```python
def load_datasets(self, dataset_files: List[str]) -> bool:
    """
    Loads JSON datasets and creates vector index

    For each dataset file:
    1. Read JSON
    2. Extract entries
    3. Combine symptom + description into text
    4. Store metadata (severity, species, etc.)
    5. Generate embeddings for all texts
    6. Build FAISS index for fast search

    Returns: True if successful, False otherwise
    """
```

**What happens:**
```python
# Example dataset entry:
{
  "symptom": "Vomiting",
  "description": "Dog is throwing up food...",
  "severity": "urgent",
  "species": "dogs",
  "home_care_india": "Keep hydrated...",
  "vet_triggers": "If vomits blood..."
}

# Combined text for embedding:
text = "Vomiting. Dog is throwing up food..."

# Generate embedding:
embedding = embedder.encode(text)  # → [0.23, -0.45, 0.12, ...] (384 numbers)

# Add to FAISS index:
index.add(embedding)
```

**FAISS Index:**
- Type: `IndexFlatIP` (Inner Product)
- Metric: Cosine similarity (after L2 normalization)
- Why: Fast similarity search across thousands of entries

#### Method: `expand_query(query)`
```python
def expand_query(self, query: str) -> str:
    """
    Expands user query with medical synonyms

    Example:
    Input:  "My dog is vomiting"
    Output: "My dog is vomiting my dog is throwing up my dog has emesis"

    Why: Improves search recall by matching different ways users describe symptoms
    """
```

**Synonym mapping:**
```python
MEDICAL_SYNONYMS = {
    'vomit': ['vomiting', 'throwing up', 'emesis'],
    'diarrhea': ['loose stool', 'loose motion', 'watery stool'],
    'pee': ['urinate', 'urine', 'urination'],
    # ... etc
}
```

#### Method: `detect_emergency(query)`
```python
def detect_emergency(self, query: str) -> bool:
    """
    Scans query for emergency keywords

    Returns True if any of these found:
    - bleeding, blood
    - seizure, unconscious
    - not breathing, collapsed
    - severe pain, bloat
    - poisoning, trauma
    - snake bite, broken bone
    - can't stand, blue gums
    """
```

**Used for:**
- Flagging urgent cases in metadata
- Adjusting LLM prompt to stress urgency
- Setting appropriate `urgency_level` in response

#### Method: `search(query, species, top_k)`
```python
def search(self, query: str, species: str = None, top_k: int = 10) -> List[Dict]:
    """
    Searches for relevant dataset entries

    Steps:
    1. Expand query with synonyms
    2. Generate query embedding
    3. Search FAISS index for similar entries
    4. Filter by species if specified
    5. Apply severity boosting
    6. Sort by final score
    7. Return top K results
    """
```

**Severity boosting:**
```python
SEVERITY_BOOST = {
    "emergency": 1.5,   # Boost emergency cases by 50%
    "urgent": 1.2,      # Boost urgent cases by 20%
    "routine": 1.0      # No boost for routine
}

# Example:
base_score = 0.75
severity = "emergency"
final_score = 0.75 * 1.5 = 1.125
```

**Why boost?**: Prioritizes serious conditions even if similarity score is slightly lower

#### Method: `generate_response(pet_details, query, matched_entries)`
```python
def generate_response(self, pet_details, query, matched_entries) -> Dict:
    """
    Generates AI response using Google Gemini

    1. Build context from top 3 matches
    2. Build pet details summary
    3. Detect emergency status
    4. Create structured prompt
    5. Call Gemini API
    6. Parse JSON response
    7. Add metadata
    8. Return structured result

    Returns: Dict with all analysis fields
    """
```

**Prompt structure:**
```python
prompt = f"""
You are a veterinary AI assistant for SNOUTIQ.

PET DETAILS:
{pet_name}, {species}, {breed}, {age}...

PET PARENT'S QUERY:
{query}

RELEVANT MEDICAL INFORMATION:
Match 1: {symptom} - {description}
Match 2: {symptom} - {description}
Match 3: {symptom} - {description}

EMERGENCY STATUS: {is_emergency}

Generate JSON response with:
- summary
- what_we_found
- immediate_steps
- home_care_tips
- when_to_see_vet
- urgency_level
- service_recommendation
- confidence
"""
```

**JSON parsing:**
- Uses regex to extract JSON from LLM response
- Falls back to template response if parsing fails
- Validates required fields exist

#### Method: `_create_fallback_response(pet_details, matched_entries, is_emergency)`
```python
def _create_fallback_response(...) -> Dict:
    """
    Creates safe default response when LLM fails

    Uses:
    - Top match metadata if available
    - Generic safe advice if no matches
    - Always recommends professional consultation
    - Sets confidence to "low"
    """
```

**When used:**
- LLM API error
- JSON parsing failure
- No matches found in database
- Network timeout

#### Method: `process_query(pet_details, query)`
```python
def process_query(self, pet_details, query) -> Dict:
    """
    Main entry point for symptom analysis

    1. Extract species from pet_details
    2. Normalize to "dogs" or "cats"
    3. Search for matching entries
    4. Generate AI response
    5. Return complete analysis
    """
```

**Species normalization:**
```python
species = pet_details.get('species', '').lower()
if 'dog' in species:
    species = 'dogs'
elif 'cat' in species:
    species = 'cats'
else:
    species = None  # Search all species
```

---

## 🔄 Data Flow

### Complete Request Flow:

```
1. User submits form on PHP frontend
   ↓
2. PHP makes HTTP POST to /query endpoint
   {
     "name": "Bruno",
     "species": "Dog",
     "query": "vomiting blood"
   }
   ↓
3. Flask validates request
   - Check required fields ✓
   - Validate species ✓
   - Validate query length ✓
   ↓
4. Extract pet_details dictionary
   {
     "name": "Bruno",
     "species": "Dog",
     "breed": "Mixed",
     ...
   }
   ↓
5. Call rag_system.process_query()
   ↓
6. Normalize species: "Dog" → "dogs"
   ↓
7. Expand query
   "vomiting blood" → "vomiting blood throwing up blood emesis blood"
   ↓
8. Generate query embedding
   Text → [0.12, -0.34, 0.56, ...] (384 numbers)
   ↓
9. Search FAISS index
   Find top 20 similar entries
   ↓
10. Filter by species = "dogs"
    Keep only dog-specific entries
    ↓
11. Apply severity boosting
    Emergency entries get 1.5x score
    ↓
12. Sort by final score, take top 10
    ↓
13. Build context from top 3 matches
    ↓
14. Detect emergency: "blood" found → TRUE
    ↓
15. Create prompt for Gemini
    Include:
    - Pet details
    - Query
    - Top 3 matches
    - Emergency flag
    ↓
16. Call Gemini API
    Get text response
    ↓
17. Parse JSON from response
    Extract structured data
    ↓
18. Add query metadata
    - timestamp
    - num_matches
    - is_emergency
    - top_match_score
    ↓
19. Return to Flask
    ↓
20. Flask wraps in success response
    {
      "success": true,
      "data": {...}
    }
    ↓
21. Send HTTP 200 response to PHP
    ↓
22. PHP displays results to user
```

---

## 🤖 ML Models Used

### 1. Sentence Transformer: all-MiniLM-L6-v2

**Purpose**: Convert text to numerical vectors (embeddings)

**Specifications:**
- **Model size**: ~80MB
- **Output dimensions**: 384
- **Max sequence length**: 256 tokens
- **Speed**: ~100 sentences/second on CPU
- **Training**: Trained on 1 billion sentence pairs

**How it works:**
```python
# Input text
text = "Dog is vomiting and has diarrhea"

# Generate embedding
embedding = model.encode(text)

# Output: Array of 384 numbers
[0.0234, -0.1234, 0.5678, ..., -0.0912]
```

**Why this model:**
- Fast inference on CPU (no GPU needed)
- Good balance of quality vs. speed
- Optimized for semantic similarity
- Multilingual capability

**Performance:**
- Initialization: ~3 seconds
- Encoding single query: ~50ms
- Encoding 1000 documents: ~10 seconds

### 2. Google Gemini 2.0 Flash

**Purpose**: Generate natural language responses

**Specifications:**
- **Model**: gemini-2.0-flash
- **Context window**: 1 million tokens
- **Response time**: 1-3 seconds
- **Capabilities**:
  - Structured output (JSON)
  - Long context understanding
  - Multilingual
  - Instruction following

**API Configuration:**
```python
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

response = model.generate_content(prompt)
text = response.text
```

**Prompt Engineering:**
- Clear role definition ("veterinary AI assistant")
- Structured input (pet details, query, matches)
- Explicit output format (JSON schema)
- Safety instructions (stress urgency for emergencies)
- India-specific context

**Why Gemini:**
- Fast response times
- Good JSON output
- Understands medical context
- Free tier available
- Reliable API

### 3. FAISS: Facebook AI Similarity Search

**Purpose**: Fast vector similarity search

**Index type**: `IndexFlatIP` (Inner Product)

**Configuration:**
```python
import faiss

dimension = 384  # Match embedding size
index = faiss.IndexFlatIP(dimension)

# Add vectors
index.add(embeddings.astype('float32'))

# Search
scores, indices = index.search(query_embedding, k=10)
```

**How it works:**
1. Stores all embeddings in memory
2. Computes cosine similarity for query
3. Returns top K most similar
4. Uses optimized BLAS operations

**Performance:**
- Search 10,000 entries: ~10ms
- Search 100,000 entries: ~100ms
- Memory: ~1.5MB per 1000 vectors (384-dim)

**Why FAISS:**
- Extremely fast
- Exact search (no approximation)
- CPU-friendly
- Battle-tested (used by production systems)

---

## 📊 Database Structure

### Dataset JSON Format

Each dataset file contains entries in this format:

```json
{
  "entries": [
    {
      "symptom": "Vomiting",
      "description": "Dog regurgitates food or liquid...",
      "severity": "urgent",
      "species": "dogs",
      "home_care_india": "Withhold food for 12-24 hours...",
      "vet_triggers": "Vomits blood, more than 3 times in 24 hours...",
      "service_recommendation": "video_consult",
      "indian_climate_factors": "Dehydration risk higher in hot weather...",
      "category": "digestive"
    }
  ]
}
```

**Field descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `symptom` | string | Yes | Short symptom name |
| `description` | string | Yes | Detailed explanation |
| `severity` | enum | Yes | emergency / urgent / routine |
| `species` | enum | Yes | dogs / cats / both |
| `home_care_india` | string | Yes | India-specific home care advice |
| `vet_triggers` | string | Yes | When to see a veterinarian |
| `service_recommendation` | enum | No | in_clinic / video_consult |
| `indian_climate_factors` | string | No | Climate considerations |
| `category` | string | Auto | Added from filename |

### Dataset Categories

1. **Emergency** (~100 entries)
   - Life-threatening conditions
   - Immediate attention needed
   - Examples: Bloat, seizures, poisoning

2. **Digestive** (~80 entries)
   - GI issues
   - Examples: Vomiting, diarrhea, constipation

3. **Respiratory** (~75 entries)
   - Breathing problems
   - Examples: Coughing, wheezing, difficulty breathing

4. **Urinary** (~70 entries)
   - Urination issues
   - Examples: Frequent urination, blood in urine

5. **Joint/Mobility** (~85 entries)
   - Movement problems
   - Examples: Limping, arthritis, paralysis

6. **Reproductive** (~75 entries)
   - Breeding and reproductive health
   - Examples: Pregnancy complications, heat cycles

7. **Skin/Coat** (~80 entries)
   - Dermatological issues
   - Examples: Itching, hair loss, rashes

8. **Eyes/Ears** (~60 entries)
   - Sensory organ problems
   - Examples: Eye discharge, ear infections

9. **Behavioral** (~50 entries)
   - Behavioral changes
   - Examples: Aggression, anxiety, lethargy

10. **Nutrition/Weight** (~20 entries)
    - Diet and weight issues
    - Examples: Obesity, malnutrition

11. **General Pet Health** (~700 entries)
    - Comprehensive health information

**Total**: ~1,395 entries across 11 datasets

### Vector Index Structure

```python
# In-memory structure after loading:

documents = [
    "Vomiting. Dog regurgitates food...",
    "Diarrhea. Loose or watery stool...",
    ...  # 1,395 entries
]

metadata = [
    {
        "symptom": "Vomiting",
        "severity": "urgent",
        "species": "dogs",
        "category": "digestive",
        ...
    },
    ...  # 1,395 entries
]

# FAISS index (not directly accessible, binary format)
index = FlatIndexIP(384)  # 1,395 x 384 matrix
```

**Memory usage:**
- Documents: ~2MB (strings)
- Metadata: ~1MB (dicts)
- FAISS index: ~2MB (vectors)
- Total: ~5MB for data, ~500MB for models

---

## ⚡ Performance Optimization

### 1. Model Loading (Startup)

**Current approach:**
```python
# Loads on server start (one-time cost)
embedder = SentenceTransformer('all-MiniLM-L6-v2')
```

**Optimization options:**
- Pre-download model to local cache
- Use Docker image with pre-loaded models
- Share models across workers

### 2. Vector Search

**Current:** FAISS IndexFlatIP (exact search)

**Optimizations for scale:**
```python
# For >100k entries, use approximate search:
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
index.train(embeddings)
index.add(embeddings)
index.nprobe = 10  # Search 10 clusters
```

**Trade-offs:**
- Exact: Slower but perfect accuracy
- Approximate: Faster but 95-98% accuracy

### 3. Caching

**Add caching for common queries:**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query_hash):
    return rag_system.search(query)
```

**Benefits:**
- Instant response for repeated queries
- Reduces API calls to Gemini
- Lower costs

### 4. Batch Processing

**For multiple queries:**
```python
# Embed multiple queries at once
queries = ["query1", "query2", "query3"]
embeddings = embedder.encode(queries)  # Faster than 3 separate calls
```

### 5. Async Processing

**For high load:**
```python
from flask import Flask
import asyncio

# Make Gemini calls async
async def generate_async(prompt):
    response = await llm.generate_content_async(prompt)
    return response.text
```

### 6. Connection Pooling

**For database-backed storage:**
```python
# If moving to PostgreSQL + pgvector
from sqlalchemy import create_engine
engine = create_engine(
    'postgresql://...',
    pool_size=10,
    max_overflow=20
)
```

### 7. Monitoring

**Add performance tracking:**
```python
import time

def log_performance(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__}: {duration:.2f}s")
        return result
    return wrapper

@log_performance
def process_query(pet_details, query):
    ...
```

---

## 🔐 Security Considerations

### 1. API Key Protection

```python
# ✅ Good: Use environment variables
api_key = os.getenv('GEMINI_API_KEY')

# ❌ Bad: Hardcode in source
api_key = "AIzaSyC..."  # Never do this!
```

### 2. Input Validation

```python
# Prevent injection attacks
def sanitize_input(text):
    # Remove potentially dangerous characters
    text = re.sub(r'[<>{}]', '', text)
    # Limit length
    text = text[:1000]
    return text
```

### 3. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/query')
@limiter.limit("10 per minute")
def process_query():
    ...
```

### 4. HTTPS Only

```nginx
# Nginx config
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Redirect HTTP to HTTPS
    if ($scheme != "https") {
        return 301 https://$server_name$request_uri;
    }
}
```

### 5. CORS Configuration

```python
# Restrict to specific domains
CORS(app, origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
])
```

---

## 📈 Scalability Considerations

### Current Limitations:

1. **In-memory FAISS index**
   - Limit: ~1 million vectors on 8GB RAM
   - Current: ~1,400 vectors (plenty of room)

2. **Single-threaded Gunicorn**
   - Can handle ~100 requests/minute
   - For more: Add workers (`--workers 4`)

3. **Gemini API rate limits**
   - Free tier: 60 requests/minute
   - Paid tier: Higher limits

### Scaling Strategies:

#### Vertical Scaling (Bigger Server)
```
4GB RAM  → 8GB RAM  → 16GB RAM
2 cores  → 4 cores  → 8 cores
```

#### Horizontal Scaling (More Servers)
```
Load Balancer
    ↓
[Server 1] [Server 2] [Server 3]
    ↓
Shared Database (if needed)
```

#### Database Migration
```python
# Move from in-memory to PostgreSQL + pgvector
from pgvector.sqlalchemy import Vector

class SymptomEntry(Base):
    __tablename__ = 'symptoms'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    embedding = Column(Vector(384))
```

#### Caching Layer
```
User → Nginx → Redis Cache → Flask → Gemini
                    ↓
                (90% hit rate)
```

---

## 🧪 Testing

### Unit Tests

```python
# test_rag_system.py
import pytest
from rag_system import SnoutiqRAG

def test_query_expansion():
    rag = SnoutiqRAG(api_key="test")
    expanded = rag.expand_query("dog vomiting")
    assert "throwing up" in expanded

def test_emergency_detection():
    rag = SnoutiqRAG(api_key="test")
    assert rag.detect_emergency("bleeding heavily") == True
    assert rag.detect_emergency("mild cough") == False
```

### Integration Tests

```python
def test_full_query():
    pet_details = {
        "name": "Test Dog",
        "species": "Dog",
        "query": "vomiting"
    }

    response = client.post('/query', json=pet_details)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'urgency_level' in data['data']
```

### Load Testing

```bash
# Using Apache Bench
ab -n 100 -c 10 -p query.json -T application/json \
   http://localhost:5000/query

# Results show:
# Requests per second: 15-20
# Average response time: 500-700ms
```

---

## 📚 Additional Resources

### Dependencies Documentation:

- **Flask**: https://flask.palletsprojects.com/
- **Sentence Transformers**: https://www.sbert.net/
- **FAISS**: https://github.com/facebookresearch/faiss
- **Google Gemini**: https://ai.google.dev/docs
- **Gunicorn**: https://gunicorn.org/

### ML/AI Concepts:

- **RAG (Retrieval-Augmented Generation)**: Combines retrieval with generation
- **Embeddings**: Numerical representations of text
- **Vector Similarity**: Measuring closeness of embeddings
- **Semantic Search**: Understanding meaning, not just keywords

---

*Technical Documentation Version 1.0 - Last Updated: October 2024*
