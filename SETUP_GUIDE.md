# 🚀 Quick Setup Guide

Follow these steps to get SNOUTIQ running in 5 minutes!

## ✅ Step-by-Step Setup

### 1️⃣ Get Your API Key (2 minutes)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 2️⃣ Add Your Dataset Files (1 minute)

Copy your 11 JSON dataset files to:
```
backend/datasets/
```

Required files:
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

### 3️⃣ Setup Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any text editor
```

In `.env` file, replace:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

With your actual API key:
```
GEMINI_API_KEY=AIzaSyC...your_actual_key
```

### 4️⃣ Start Backend

```bash
python app.py
```

Wait for:
```
✅ System ready with X entries!
🚀 Starting SNOUTIQ API on port 5000
```

### 5️⃣ Start Frontend

Open **NEW terminal**:

```bash
cd frontend
php -S localhost:8000
```

### 6️⃣ Open in Browser

Go to: **http://localhost:8000**

## 🎉 You're Done!

Fill in the form and test with this example:

- **Pet Name**: Bruno
- **Species**: Dog
- **Breed**: Labrador
- **Query**: "My dog has been vomiting since this morning and seems very weak"

Click "Analyze Symptoms" and watch the magic! ✨

## ❓ Having Issues?

### Backend won't start?
- Check Python version: `python --version` (need 3.8+)
- Check if datasets folder has JSON files
- Check if API key is correct in `.env`

### Frontend shows "Failed to connect"?
- Is backend running? Check `http://localhost:5000/health`
- Check API_URL in `frontend/index.php` line 374

### Need help?
Check the main README.md for detailed troubleshooting!

---

**Happy Testing! 🐾**
