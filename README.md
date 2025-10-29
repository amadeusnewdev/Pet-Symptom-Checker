# 🐾 SNOUTIQ - AI-Powered Veterinary Symptom Checker

A production-ready veterinary symptom checker using **RAG (Retrieval-Augmented Generation)** technology, powered by Google Gemini and advanced embeddings.

## 🌟 Features

- **Advanced RAG System**: Combines vector search with LLM for accurate symptom analysis
- **Medical Knowledge Base**: 10+ specialized veterinary datasets (emergency, digestive, respiratory, etc.)
- **Smart Query Expansion**: Automatically expands queries with medical synonyms
- **Emergency Detection**: Identifies critical situations requiring immediate attention
- **India-Specific**: Tailored for Indian climate, medications, and veterinary practices
- **Species-Aware**: Optimized for both dogs and cats
- **Beautiful UI**: Professional, responsive PHP frontend
- **Production-Ready API**: Flask backend with proper error handling, validation, and logging

## 📁 Project Structure

```
Pet-Symptom-Checker/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── rag_system.py          # Core RAG system logic
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment variables template
│   └── datasets/              # Veterinary knowledge base (JSON files)
│       ├── master_emergency_dataset.json
│       ├── master_digestive_dataset.json
│       ├── master_respiratory_dataset.json
│       └── ... (add your 11 dataset files here)
├── frontend/
│   └── index.php              # PHP frontend with form
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **PHP 7.4+** (with web server like Apache/Nginx, or use PHP's built-in server)
- **Google Gemini API Key** (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Pet-Symptom-Checker.git
cd Pet-Symptom-Checker
```

### Step 2: Add Dataset Files

**IMPORTANT**: Place your 11 dataset JSON files in the `backend/datasets/` folder:

```bash
backend/datasets/
├── master_emergency_dataset.json
├── master_digestive_dataset.json
├── master_respiratory_dataset.json
├── master_urinary_dataset.json
├── master_joint_mobility_dataset.json
├── master_reproductive_dataset.json
├── master_skin_coat_dataset.json
├── master_eyes_ears_dataset.json
├── master_behavioral_dataset.json
├── master_nutrition_weight_dataset.json
└── (any other datasets)
```

### Step 3: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your Gemini API key
nano .env  # or use any text editor
```

**Edit `.env` file:**
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_ENV=development
PORT=5000
```

### Step 4: Start the Backend API

```bash
# Make sure you're in the backend directory with venv activated
python app.py
```

You should see:
```
🚀 Initializing SNOUTIQ RAG System...
📊 Loading AI models...
✅ Models loaded successfully
📚 Loading veterinary datasets...
   ✓ emergency: X entries
   ✓ digestive: X entries
   ...
🔄 Creating embeddings for X entries...
✅ System ready with X entries!
🚀 Starting SNOUTIQ API on port 5000
```

### Step 5: Start the Frontend

Open a **new terminal** window:

```bash
cd frontend

# Option 1: Using PHP built-in server (simplest)
php -S localhost:8000

# Option 2: Using Apache/Nginx (configure document root to frontend/)
```

### Step 6: Access the Application

Open your browser and go to:
```
http://localhost:8000
```

## 🧪 Testing the API

### Health Check

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "SNOUTIQ API",
  "rag_loaded": true
}
```

### Dataset Info

```bash
curl http://localhost:5000/datasets/info
```

### Test Query (using curl)

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bruno",
    "species": "Dog",
    "breed": "Labrador",
    "age": "5 years",
    "weight": "32 kg",
    "sex": "Male",
    "vaccination_summary": "Up to date",
    "medical_history": "No major issues",
    "query": "My dog has been vomiting since morning and seems weak"
  }'
```

## 🔧 Configuration

### Backend Configuration (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | ✅ Yes |
| `FLASK_ENV` | Environment (development/production) | No (default: development) |
| `PORT` | API server port | No (default: 5000) |

### Frontend Configuration

Edit the `API_URL` in `frontend/index.php` (line 374):

```javascript
const API_URL = 'http://localhost:5000/query';
```

For production, change to your production API URL:
```javascript
const API_URL = 'https://api.youromain.com/query';
```

## 📊 Models Used

- **Embedding Model**: `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **LLM Model**: `gemini-2.0-flash` (Google Gemini)
- **Vector Search**: FAISS (Facebook AI Similarity Search)

## 🎯 API Endpoints

### POST `/query`

Analyze pet symptoms and get AI-powered recommendations.

**Request Body:**
```json
{
  "name": "Pet name",
  "species": "Dog/Cat",
  "breed": "Breed (optional)",
  "age": "Age (optional)",
  "weight": "Weight (optional)",
  "sex": "Male/Female (optional)",
  "vaccination_summary": "Vaccination status (optional)",
  "medical_history": "Medical history (optional)",
  "query": "Symptom description (required)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pet_name": "Bruno",
    "summary": "Brief summary of the situation",
    "what_we_found": "Detailed explanation",
    "immediate_steps": ["Step 1", "Step 2", "Step 3"],
    "home_care_tips": ["Tip 1", "Tip 2", "Tip 3"],
    "when_to_see_vet": "Criteria for vet visit",
    "urgency_level": "emergency/urgent/routine",
    "service_recommendation": "in_clinic/video_consult",
    "confidence": "high/medium/low",
    "additional_notes": "Breed/age/climate specific notes",
    "query_metadata": {
      "timestamp": "2024-01-01T12:00:00",
      "num_matches": 10,
      "is_emergency": false,
      "top_match_score": 0.85
    }
  }
}
```

### GET `/health`

Check API health status.

### GET `/datasets/info`

Get information about loaded datasets.

## 🚨 Emergency Detection

The system automatically detects emergency keywords:
- bleeding, blood, seizure, unconscious
- not breathing, collapsed, severe pain
- bloat, poisoning, trauma
- snake bite, broken bone, can't stand, blue gums

Emergency queries receive:
- Higher urgency level
- Immediate vet visit recommendation
- Prioritized emergency care steps

## 🔍 How It Works

1. **Query Expansion**: User query is expanded with medical synonyms
2. **Vector Search**: FAISS finds top 10 most relevant entries from knowledge base
3. **Species Filtering**: Results filtered by pet species (dog/cat)
4. **Severity Boosting**: Emergency cases get 1.5x boost, urgent 1.2x
5. **Context Building**: Top 3 matches compiled into context
6. **LLM Generation**: Gemini generates personalized response
7. **Structured Output**: JSON response with actionable advice

## 📦 Production Deployment

### Using Gunicorn (Production Server)

```bash
# Already included in requirements.txt
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### Environment Variables for Production

```env
GEMINI_API_KEY=your_key_here
FLASK_ENV=production
PORT=8080
```

### CORS Configuration

CORS is enabled by default for all origins. For production, modify `backend/app.py`:

```python
CORS(app, origins=["https://yourdomain.com"])
```

## 🛠️ Troubleshooting

### Backend won't start
- **Check Python version**: `python --version` (must be 3.8+)
- **Check API key**: Verify `GEMINI_API_KEY` in `.env`
- **Check datasets**: Ensure JSON files are in `backend/datasets/`
- **Check dependencies**: `pip install -r requirements.txt`

### Frontend can't connect to API
- **Check backend is running**: Visit `http://localhost:5000/health`
- **Check CORS**: Ensure CORS is enabled in `app.py`
- **Check API_URL**: Verify URL in `frontend/index.php`
- **Check browser console**: Look for error messages

### Low quality responses
- **Check dataset quality**: Ensure JSON files are properly formatted
- **Check API key**: Verify Gemini API key is valid
- **Check query detail**: More detailed queries get better results

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Google Gemini** for powerful LLM capabilities
- **Sentence Transformers** for embedding models
- **FAISS** for efficient vector search
- **Flask** for robust API framework

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**⚠️ Disclaimer**: This is an AI-powered advisory tool. Always consult a licensed veterinarian for professional diagnosis and treatment.

**Made with ❤️ for pets in India**
