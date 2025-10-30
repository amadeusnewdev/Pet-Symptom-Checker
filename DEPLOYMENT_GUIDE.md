# 🚀 SNOUTIQ Production Deployment Guide

**Complete guide for deploying the RAG-based veterinary symptom checker on a production VPS**

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Server Requirements](#server-requirements)
3. [Installation Steps](#installation-steps)
4. [API Documentation](#api-documentation)
5. [PHP Frontend Integration](#php-frontend-integration)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## 🎯 System Overview

### What is SNOUTIQ?

SNOUTIQ is an AI-powered veterinary symptom checker that uses:
- **RAG (Retrieval-Augmented Generation)** technology
- **Google Gemini AI** for generating responses
- **Sentence Transformers** for semantic search
- **FAISS** for vector similarity search
- **11 veterinary datasets** covering various pet health conditions

### How it Works:

```
User submits pet details + symptoms
    ↓
Backend searches 11 datasets using AI embeddings
    ↓
Top matching symptoms retrieved
    ↓
Google Gemini generates personalized advice
    ↓
Returns structured JSON response with recommendations
```

### Architecture:

```
PHP Frontend (Your existing site)
         ↓ HTTP POST
Flask API Backend (Port 5000)
         ↓
  RAG System (Python)
         ↓
  Google Gemini API
         ↓
  JSON Response
```

---

## 🖥️ Server Requirements

### Minimum Specifications:

- **OS**: Ubuntu 20.04 LTS or newer / CentOS 7+ / Debian 10+
- **RAM**: **4GB minimum, 8GB recommended** (for ML models)
- **Storage**: 10GB free space
- **CPU**: 2+ cores
- **Python**: 3.8 or higher
- **Network**: Open port 5000 (or custom port)

### Required Software:

```bash
- Python 3.8+
- pip (Python package manager)
- virtualenv (recommended)
- Nginx or Apache (for reverse proxy - optional but recommended)
```

---

## 📦 Installation Steps

### Step 1: Connect to Your VPS

```bash
ssh root@your-server-ip
# or
ssh username@your-server-ip
```

### Step 2: Update System

```bash
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# OR
sudo yum update -y  # CentOS
```

### Step 3: Install Python 3.11

```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv python3-pip -y

# CentOS
sudo yum install python3.11 python3.11-venv python3-pip -y

# Verify installation
python3.11 --version
```

### Step 4: Clone the Repository

```bash
cd /var/www/
git clone https://github.com/amadeusnewdev/Pet-Symptom-Checker.git
cd Pet-Symptom-Checker
```

**OR** upload files via FTP/SFTP to `/var/www/Pet-Symptom-Checker/`

### Step 5: Create Virtual Environment

```bash
cd /var/www/Pet-Symptom-Checker
python3.11 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 6: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏱️ **This will take 15-30 minutes** - downloading ~3GB of ML libraries (PyTorch, Transformers, etc.)

### Step 7: Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add these lines:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
FLASK_ENV=production
PORT=5000
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

**Get Gemini API Key**: https://makersuite.google.com/app/apikey

### Step 8: Test the Backend

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start the server
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
✅ System ready with X entries!
🚀 Starting SNOUTIQ API on port 5000
```

**Test it**: Open browser → `http://your-server-ip:5000/health`

You should see:

```json
{
  "status": "healthy",
  "service": "SNOUTIQ API",
  "rag_loaded": true
}
```

✅ **If `rag_loaded: true` - SUCCESS!**

Press `Ctrl+C` to stop the test server.

### Step 9: Setup as a System Service (Auto-start on boot)

Create systemd service file:

```bash
sudo nano /etc/systemd/system/snoutiq.service
```

Add this content:

```ini
[Unit]
Description=SNOUTIQ Flask API Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/Pet-Symptom-Checker
Environment="PATH=/var/www/Pet-Symptom-Checker/venv/bin"
ExecStart=/var/www/Pet-Symptom-Checker/venv/bin/gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --timeout 120
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save** and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable snoutiq
sudo systemctl start snoutiq
sudo systemctl status snoutiq
```

You should see: `Active: active (running)`

### Step 10: Setup Nginx Reverse Proxy (Optional but Recommended)

Install Nginx:

```bash
sudo apt install nginx -y  # Ubuntu/Debian
# OR
sudo yum install nginx -y  # CentOS
```

Create Nginx config:

```bash
sudo nano /etc/nginx/sites-available/snoutiq
```

Add this:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
```

Enable and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/snoutiq /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

Now your API is accessible at: `http://your-domain.com/health`

---

## 📡 API Documentation

### Base URL

```
http://your-server-ip:5000
# OR (with Nginx)
http://your-domain.com
```

### Endpoints

#### 1. Health Check

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "SNOUTIQ API",
  "rag_loaded": true
}
```

---

#### 2. Dataset Info

**GET** `/datasets/info`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_entries": 1234,
    "embedding_model": "all-MiniLM-L6-v2",
    "llm_model": "gemini-2.0-flash"
  }
}
```

---

#### 3. Symptom Analysis (Main Endpoint)

**POST** `/query`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Bruno",
  "species": "Dog",
  "breed": "Labrador Retriever",
  "age": "5 years",
  "weight": "32 kg",
  "sex": "Male",
  "vaccination_summary": "Up to date - last vaccinated 6 months ago",
  "medical_history": "No major health issues",
  "query": "My dog has been vomiting since morning and seems very weak"
}
```

**Required Fields:**
- `name` (string)
- `species` (string: "Dog" or "Cat")
- `query` (string: minimum 10 characters)

**Optional Fields:**
- `breed` (default: "Mixed")
- `age` (default: "Unknown")
- `weight` (default: "Unknown")
- `sex` (default: "Unknown")
- `vaccination_summary` (default: "Not provided")
- `medical_history` (default: "No history provided")

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "pet_name": "Bruno",
    "summary": "Brief 1-2 sentence summary of the situation",
    "what_we_found": "Detailed explanation based on symptoms and medical history",
    "immediate_steps": [
      "Step 1: What to do right now",
      "Step 2: How to monitor",
      "Step 3: What to avoid"
    ],
    "home_care_tips": [
      "Tip 1: Specific care advice",
      "Tip 2: What to watch for",
      "Tip 3: How to make pet comfortable"
    ],
    "when_to_see_vet": "Clear criteria for when veterinary care is needed",
    "urgency_level": "emergency",
    "service_recommendation": "in_clinic",
    "confidence": "high",
    "additional_notes": "Breed-specific or climate considerations",
    "query_metadata": {
      "timestamp": "2024-01-01T12:00:00",
      "num_matches": 10,
      "is_emergency": true,
      "top_match_score": 0.85
    }
  }
}
```

**Urgency Levels:**
- `emergency` - Immediate vet visit required
- `urgent` - Vet visit within 24 hours
- `routine` - Can monitor at home, see vet if worsens

**Service Recommendations:**
- `in_clinic` - Visit vet clinic immediately
- `video_consult` - Can start with online consultation

**Confidence Levels:**
- `high` - Strong match with symptoms in database
- `medium` - Moderate match
- `low` - Uncertain, professional assessment recommended

**Error Response (400 Bad Request):**

```json
{
  "success": false,
  "error": "Missing required field: query"
}
```

**Error Response (503 Service Unavailable):**

```json
{
  "success": false,
  "error": "RAG system not initialized"
}
```

---

## 🔗 PHP Frontend Integration

### Example 1: Simple PHP Form Submission

```php
<?php
// config.php
define('SNOUTIQ_API_URL', 'http://your-server-ip:5000/query');
// OR with domain:
// define('SNOUTIQ_API_URL', 'http://api.yourdomain.com/query');

// process_symptom.php
<?php
require_once 'config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Collect form data
    $data = [
        'name' => $_POST['pet_name'] ?? '',
        'species' => $_POST['species'] ?? '',
        'breed' => $_POST['breed'] ?? 'Mixed',
        'age' => $_POST['age'] ?? 'Unknown',
        'weight' => $_POST['weight'] ?? 'Unknown',
        'sex' => $_POST['sex'] ?? 'Unknown',
        'vaccination_summary' => $_POST['vaccination'] ?? 'Not provided',
        'medical_history' => $_POST['medical_history'] ?? 'No history provided',
        'query' => $_POST['symptoms'] ?? ''
    ];

    // Validate required fields
    if (empty($data['name']) || empty($data['species']) || empty($data['query'])) {
        die('Error: Please fill in all required fields');
    }

    // Call SNOUTIQ API
    $ch = curl_init(SNOUTIQ_API_URL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);
    curl_setopt($ch, CURLOPT_TIMEOUT, 60); // 60 seconds timeout

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($httpCode !== 200) {
        die('Error: API request failed');
    }

    $result = json_decode($response, true);

    if ($result['success']) {
        $analysis = $result['data'];

        // Display results
        echo "<h2>Analysis for " . htmlspecialchars($analysis['pet_name']) . "</h2>";
        echo "<p><strong>Summary:</strong> " . htmlspecialchars($analysis['summary']) . "</p>";
        echo "<p><strong>What We Found:</strong> " . htmlspecialchars($analysis['what_we_found']) . "</p>";

        echo "<h3>Immediate Steps:</h3><ul>";
        foreach ($analysis['immediate_steps'] as $step) {
            echo "<li>" . htmlspecialchars($step) . "</li>";
        }
        echo "</ul>";

        echo "<h3>Home Care Tips:</h3><ul>";
        foreach ($analysis['home_care_tips'] as $tip) {
            echo "<li>" . htmlspecialchars($tip) . "</li>";
        }
        echo "</ul>";

        echo "<p><strong>When to See Vet:</strong> " . htmlspecialchars($analysis['when_to_see_vet']) . "</p>";
        echo "<p><strong>Urgency:</strong> " . strtoupper($analysis['urgency_level']) . "</p>";
        echo "<p><strong>Recommendation:</strong> " . str_replace('_', ' ', strtoupper($analysis['service_recommendation'])) . "</p>";

    } else {
        echo "Error: " . htmlspecialchars($result['error']);
    }
}
?>
```

### Example 2: HTML Form

```html
<!-- symptom_form.php -->
<!DOCTYPE html>
<html>
<head>
    <title>SNOUTIQ - Pet Symptom Checker</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        textarea { min-height: 100px; }
        button { background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
        .required { color: red; }
    </style>
</head>
<body>
    <h1>🐾 SNOUTIQ Pet Symptom Checker</h1>

    <form action="process_symptom.php" method="POST">
        <div class="form-group">
            <label>Pet Name <span class="required">*</span></label>
            <input type="text" name="pet_name" required placeholder="e.g., Bruno">
        </div>

        <div class="form-group">
            <label>Species <span class="required">*</span></label>
            <select name="species" required>
                <option value="">Select Species</option>
                <option value="Dog">Dog</option>
                <option value="Cat">Cat</option>
            </select>
        </div>

        <div class="form-group">
            <label>Breed</label>
            <input type="text" name="breed" placeholder="e.g., Labrador Retriever">
        </div>

        <div class="form-group">
            <label>Age</label>
            <input type="text" name="age" placeholder="e.g., 5 years">
        </div>

        <div class="form-group">
            <label>Weight</label>
            <input type="text" name="weight" placeholder="e.g., 32 kg">
        </div>

        <div class="form-group">
            <label>Sex</label>
            <select name="sex">
                <option value="">Select</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
            </select>
        </div>

        <div class="form-group">
            <label>Vaccination Status</label>
            <input type="text" name="vaccination" placeholder="e.g., Up to date">
        </div>

        <div class="form-group">
            <label>Medical History</label>
            <textarea name="medical_history" placeholder="Any previous health issues..."></textarea>
        </div>

        <div class="form-group">
            <label>Describe Symptoms <span class="required">*</span></label>
            <textarea name="symptoms" required placeholder="Describe what symptoms your pet is experiencing..."></textarea>
        </div>

        <button type="submit">Analyze Symptoms</button>
    </form>
</body>
</html>
```

### Example 3: AJAX Request (jQuery)

```javascript
// Using jQuery
$('#symptomForm').on('submit', function(e) {
    e.preventDefault();

    var formData = {
        name: $('#pet_name').val(),
        species: $('#species').val(),
        breed: $('#breed').val() || 'Mixed',
        age: $('#age').val() || 'Unknown',
        weight: $('#weight').val() || 'Unknown',
        sex: $('#sex').val() || 'Unknown',
        vaccination_summary: $('#vaccination').val() || 'Not provided',
        medical_history: $('#medical_history').val() || 'No history provided',
        query: $('#symptoms').val()
    };

    $.ajax({
        url: 'http://your-server-ip:5000/query',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        timeout: 60000, // 60 seconds
        success: function(response) {
            if (response.success) {
                var data = response.data;
                // Display results
                $('#results').html(`
                    <h2>Analysis for ${data.pet_name}</h2>
                    <p><strong>Summary:</strong> ${data.summary}</p>
                    <p><strong>Urgency:</strong> ${data.urgency_level.toUpperCase()}</p>
                    <!-- Add more fields as needed -->
                `);
            } else {
                alert('Error: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            alert('Failed to connect to API: ' + error);
        }
    });
});
```

### Example 4: Using cURL from PHP (Alternative Method)

```php
<?php
function analyzeSymptoms($petData) {
    $apiUrl = 'http://your-server-ip:5000/query';

    $ch = curl_init($apiUrl);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($petData),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_TIMEOUT => 60
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curlError = curl_error($ch);
    curl_close($ch);

    if ($curlError) {
        return ['success' => false, 'error' => 'Connection failed: ' . $curlError];
    }

    if ($httpCode !== 200) {
        return ['success' => false, 'error' => 'API returned error code: ' . $httpCode];
    }

    return json_decode($response, true);
}

// Usage:
$result = analyzeSymptoms([
    'name' => 'Bruno',
    'species' => 'Dog',
    'query' => 'Vomiting since morning'
]);

if ($result['success']) {
    $data = $result['data'];
    echo "Urgency: " . $data['urgency_level'];
} else {
    echo "Error: " . $result['error'];
}
?>
```

---

## 🔧 Troubleshooting

### Problem 1: Service Won't Start

**Check logs:**
```bash
sudo journalctl -u snoutiq -n 50
```

**Common causes:**
- Missing API key in `.env`
- Virtual environment not activated
- Dataset files missing
- Port 5000 already in use

**Solution:**
```bash
# Check if port is in use
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>

# Restart service
sudo systemctl restart snoutiq
```

### Problem 2: "RAG system not initialized"

**Cause:** API key missing or invalid

**Solution:**
```bash
# Check .env file
cat /var/www/Pet-Symptom-Checker/.env

# Verify API key is correct
# Get new key from: https://makersuite.google.com/app/apikey

# Update .env
nano /var/www/Pet-Symptom-Checker/.env

# Restart service
sudo systemctl restart snoutiq
```

### Problem 3: Slow Response Times

**Cause:** First request loads AI models (30-60 seconds)

**Solution:**
- This is normal for first request
- Subsequent requests are fast (2-5 seconds)
- Consider keeping service warm with periodic health checks

**Warmup script (optional):**
```bash
# Add to crontab
*/5 * * * * curl -s http://localhost:5000/health > /dev/null
```

### Problem 4: Out of Memory

**Symptoms:** Service crashes or won't start

**Check memory:**
```bash
free -h
```

**Solution:**
- Upgrade server RAM to 4GB minimum
- Add swap space (temporary):

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Problem 5: PHP Can't Connect to API

**Check:**

```php
<?php
// test_api.php
$ch = curl_init('http://your-server-ip:5000/health');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    echo "Error: " . $error;
} else {
    echo "Response: " . $response;
}
?>
```

**Common issues:**
- Firewall blocking port 5000
- Wrong IP/domain in API URL
- curl not installed in PHP

**Solution:**
```bash
# Open firewall port
sudo ufw allow 5000/tcp

# Install PHP curl
sudo apt install php-curl -y
sudo systemctl restart apache2  # or nginx
```

---

## 🔐 Security Best Practices

### 1. Use HTTPS (SSL Certificate)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 2. Restrict API Access

Add to Nginx config:

```nginx
# Allow only your frontend server
allow your-frontend-server-ip;
deny all;
```

### 3. Add Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;

location /query {
    limit_req zone=api_limit burst=5;
    proxy_pass http://127.0.0.1:5000;
}
```

### 4. Environment Variables Security

```bash
# Restrict .env file permissions
chmod 600 /var/www/Pet-Symptom-Checker/.env
chown www-data:www-data /var/www/Pet-Symptom-Checker/.env
```

---

## 🔄 Maintenance

### Update the Application

```bash
cd /var/www/Pet-Symptom-Checker
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart snoutiq
```

### Monitor Logs

```bash
# Real-time logs
sudo journalctl -u snoutiq -f

# Last 100 lines
sudo journalctl -u snoutiq -n 100

# Logs from today
sudo journalctl -u snoutiq --since today
```

### Backup

```bash
# Backup datasets and config
tar -czf snoutiq-backup-$(date +%Y%m%d).tar.gz \
  /var/www/Pet-Symptom-Checker/datasets \
  /var/www/Pet-Symptom-Checker/.env

# Restore
tar -xzf snoutiq-backup-20240101.tar.gz -C /
```

### Check Service Status

```bash
# Status
sudo systemctl status snoutiq

# Restart
sudo systemctl restart snoutiq

# Stop
sudo systemctl stop snoutiq

# Start
sudo systemctl start snoutiq

# View resource usage
htop
```

---

## 📞 Support & Contact

### Common Commands Quick Reference

```bash
# Start service
sudo systemctl start snoutiq

# Stop service
sudo systemctl stop snoutiq

# Restart service
sudo systemctl restart snoutiq

# Check status
sudo systemctl status snoutiq

# View logs
sudo journalctl -u snoutiq -f

# Test API
curl http://localhost:5000/health

# Activate virtual environment
source /var/www/Pet-Symptom-Checker/venv/bin/activate

# Update code
cd /var/www/Pet-Symptom-Checker && git pull

# Reinstall dependencies
pip install -r requirements.txt
```

### File Locations

- **Application**: `/var/www/Pet-Symptom-Checker/`
- **Service file**: `/etc/systemd/system/snoutiq.service`
- **Nginx config**: `/etc/nginx/sites-available/snoutiq`
- **Logs**: `sudo journalctl -u snoutiq`
- **Environment**: `/var/www/Pet-Symptom-Checker/.env`

---

## ✅ Deployment Checklist

- [ ] VPS server with 4GB+ RAM ready
- [ ] Python 3.11 installed
- [ ] Code uploaded to `/var/www/Pet-Symptom-Checker/`
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with valid `GEMINI_API_KEY`
- [ ] Test server works (`python app.py`)
- [ ] `/health` endpoint returns `rag_loaded: true`
- [ ] Systemd service created and enabled
- [ ] Service starts automatically (`sudo systemctl start snoutiq`)
- [ ] Nginx reverse proxy configured (optional)
- [ ] Firewall allows port 5000
- [ ] PHP frontend can connect to API
- [ ] Test full workflow: Submit form → Get analysis
- [ ] SSL certificate installed (for production)
- [ ] Monitoring and logs configured

---

**🎉 Deployment Complete!**

Your SNOUTIQ backend is now running in production and ready to serve veterinary symptom analysis requests!

---

*Documentation Version 1.0 - Last Updated: October 2024*
