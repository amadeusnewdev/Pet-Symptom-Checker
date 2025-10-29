# Convert RAG Notebook to Production Flask API with PHP Frontend

## 🐾 SNOUTIQ - Production-Ready Veterinary Symptom Checker

Converted the working RAG Jupyter notebook into a production Flask API with professional PHP frontend.

---

## ✨ What's Included

### Backend (Flask API)
- **Flask REST API** (`backend/app.py`)
  - POST `/query` - Main symptom analysis endpoint
  - GET `/health` - Health check
  - GET `/datasets/info` - Dataset information
  - Full error handling, validation, CORS support, logging

- **Core RAG System** (`backend/rag_system.py`)
  - Same embedding model: `all-MiniLM-L6-v2`
  - Same LLM: `gemini-2.0-flash`
  - Medical synonym expansion
  - Emergency detection
  - Severity boosting (emergency 1.5x, urgent 1.2x, routine 1.0x)
  - Species filtering (dogs/cats)
  - Query expansion with medical synonyms
  - Fallback responses

- **Configuration**
  - `requirements.txt` - All Python dependencies
  - `.env.example` - API key template
  - `start.sh` / `start.bat` - Startup scripts for Linux/Mac/Windows

### Frontend (PHP)
- **Professional UI** (`frontend/index.php`)
  - Responsive design with gradient styling
  - Comprehensive pet details form
  - Real-time API integration
  - Loading states with animations
  - Structured result display with urgency badges
  - Mobile-friendly layout
  - Error handling

### Documentation
- **README.md** - Complete setup guide, API documentation, troubleshooting
- **SETUP_GUIDE.md** - Quick 5-minute setup walkthrough
- **backend/datasets/README.md** - Dataset format and instructions
- **.gitignore** - Proper exclusions for Python, env files, venv

---

## 🎯 Key Features Preserved

✅ Exact same models from original notebook
✅ All RAG parameters identical (TOP_K=10, MIN_SIMILARITY=0.3)
✅ Medical synonym expansion logic
✅ Emergency keyword detection
✅ Severity-based result boosting
✅ India-specific veterinary advice
✅ Species-aware filtering
✅ Fallback response system

---

## 📁 Project Structure

```
Pet-Symptom-Checker/
├── backend/
│   ├── app.py                 # Flask API (233 lines)
│   ├── rag_system.py          # Core RAG logic (375 lines)
│   ├── requirements.txt       # Dependencies
│   ├── .env.example          # API key template
│   ├── start.sh/start.bat    # Startup scripts
│   └── datasets/             # Add 11 JSON files here
├── frontend/
│   └── index.php             # UI (563 lines)
├── README.md
├── SETUP_GUIDE.md
└── .gitignore
```

**Total**: 11 files, 1,171 lines of code

---

## 🚀 Setup Instructions

### 1. Add Dataset Files
Place 11 JSON files in `backend/datasets/`:
- master_emergency_dataset.json
- master_digestive_dataset.json
- master_respiratory_dataset.json
- master_urinary_dataset.json
- master_joint_mobility_dataset.json
- master_reproductive_dataset.json
- master_skin_coat_dataset.json
- master_eyes_ears_dataset.json
- master_behavioral_dataset.json
- master_nutrition_weight_dataset.json
- (any other datasets)

### 2. Configure Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
```

### 3. Start Services
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
php -S localhost:8000
```

### 4. Access Application
Open browser: **http://localhost:8000**

---

## 🔧 Technical Stack

- **Python 3.8+** with Flask, FAISS, Sentence Transformers
- **Google Gemini API** (gemini-2.0-flash)
- **Embedding Model**: all-MiniLM-L6-v2 (384-dim)
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **PHP 7.4+** for frontend
- **Environment-based config** with `.env`
- **Production-ready** with gunicorn support

---

## 🧪 API Example

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bruno",
    "species": "Dog",
    "breed": "Labrador",
    "age": "5 years",
    "weight": "32 kg",
    "query": "vomiting blood since morning, very weak"
  }'
```

---

## ✅ Testing Checklist

- [ ] Add 11 dataset JSON files to `backend/datasets/`
- [ ] Create `.env` file with `GEMINI_API_KEY`
- [ ] Install Python dependencies: `pip install -r requirements.txt`
- [ ] Start backend: `python app.py`
- [ ] Start frontend: `php -S localhost:8000`
- [ ] Test with sample query in browser
- [ ] Verify emergency detection works
- [ ] Check species filtering (dog vs cat)
- [ ] Test API endpoints: `/health`, `/datasets/info`, `/query`

---

## 📝 Notes

- `.env` file is gitignored (security best practice)
- Dataset files can be added locally - not committed to avoid large repo size
- All core RAG logic preserved exactly from working notebook
- Production-ready with proper error handling and validation
- CORS enabled for frontend-backend communication

---

**Ready for testing and deployment!** 🚀
