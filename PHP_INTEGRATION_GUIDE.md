# 🐘 PHP Integration Guide for SNOUTIQ API

**Quick guide for PHP developers to integrate SNOUTIQ veterinary symptom checker into their website**

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Copy This Function to Your PHP Project

```php
<?php
/**
 * SNOUTIQ API Integration
 * Call this function to analyze pet symptoms
 */
function analyzeSymptoms($petData, $apiUrl = 'http://your-server-ip:5000/query') {
    // Initialize cURL
    $ch = curl_init($apiUrl);

    // Set cURL options
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($petData),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_TIMEOUT => 60  // 60 seconds timeout
    ]);

    // Execute request
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);

    // Handle errors
    if ($error) {
        return [
            'success' => false,
            'error' => 'Connection failed: ' . $error
        ];
    }

    if ($httpCode !== 200) {
        return [
            'success' => false,
            'error' => 'API returned error code: ' . $httpCode
        ];
    }

    // Parse and return response
    return json_decode($response, true);
}
?>
```

### Step 2: Use It in Your Form Handler

```php
<?php
// Example: process_form.php

require_once 'snoutiq_api.php';  // Include the function above

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // Prepare data for API
    $petData = [
        'name' => $_POST['pet_name'],
        'species' => $_POST['species'],        // "Dog" or "Cat"
        'breed' => $_POST['breed'] ?? 'Mixed',
        'age' => $_POST['age'] ?? 'Unknown',
        'weight' => $_POST['weight'] ?? 'Unknown',
        'sex' => $_POST['sex'] ?? 'Unknown',
        'vaccination_summary' => $_POST['vaccination'] ?? 'Not provided',
        'medical_history' => $_POST['medical_history'] ?? 'Not provided',
        'query' => $_POST['symptoms']          // Required!
    ];

    // Call SNOUTIQ API
    $result = analyzeSymptoms($petData, 'http://your-server-ip:5000/query');

    // Check result
    if ($result['success']) {
        $data = $result['data'];

        // Display results
        echo "<h2>Analysis for " . htmlspecialchars($data['pet_name']) . "</h2>";
        echo "<p><strong>Urgency:</strong> " . strtoupper($data['urgency_level']) . "</p>";
        echo "<p><strong>Summary:</strong> " . htmlspecialchars($data['summary']) . "</p>";

        // Show immediate steps
        echo "<h3>What to Do Now:</h3><ul>";
        foreach ($data['immediate_steps'] as $step) {
            echo "<li>" . htmlspecialchars($step) . "</li>";
        }
        echo "</ul>";

        // Show when to see vet
        echo "<p><strong>See Vet If:</strong> " . htmlspecialchars($data['when_to_see_vet']) . "</p>";

    } else {
        echo "Error: " . htmlspecialchars($result['error']);
    }
}
?>
```

### Step 3: Create HTML Form

```html
<!-- symptom_form.html -->
<form action="process_form.php" method="POST">
    <h2>Pet Symptom Checker</h2>

    <!-- Required fields -->
    <label>Pet Name *</label>
    <input type="text" name="pet_name" required>

    <label>Species *</label>
    <select name="species" required>
        <option value="">Select</option>
        <option value="Dog">Dog</option>
        <option value="Cat">Cat</option>
    </select>

    <label>Symptoms *</label>
    <textarea name="symptoms" required placeholder="Describe symptoms..."></textarea>

    <!-- Optional fields -->
    <label>Breed</label>
    <input type="text" name="breed">

    <label>Age</label>
    <input type="text" name="age">

    <label>Weight</label>
    <input type="text" name="weight">

    <label>Sex</label>
    <select name="sex">
        <option value="">Select</option>
        <option value="Male">Male</option>
        <option value="Female">Female</option>
    </select>

    <label>Vaccination Status</label>
    <input type="text" name="vaccination">

    <label>Medical History</label>
    <textarea name="medical_history"></textarea>

    <button type="submit">Analyze Symptoms</button>
</form>
```

---

## 📋 Complete Examples

### Example 1: WordPress Integration

```php
<?php
/**
 * Plugin Name: SNOUTIQ Symptom Checker
 * Description: AI-powered pet symptom analysis
 * Version: 1.0
 */

// Add to your theme's functions.php or create a plugin

add_shortcode('snoutiq_form', 'snoutiq_display_form');

function snoutiq_display_form() {
    ob_start();
    ?>
    <form id="snoutiq-form" method="POST" action="">
        <?php wp_nonce_field('snoutiq_submit', 'snoutiq_nonce'); ?>

        <input type="text" name="pet_name" placeholder="Pet Name" required>
        <select name="species" required>
            <option value="">Select Species</option>
            <option value="Dog">Dog</option>
            <option value="Cat">Cat</option>
        </select>
        <textarea name="symptoms" placeholder="Describe symptoms..." required></textarea>
        <button type="submit" name="snoutiq_submit">Analyze</button>
    </form>

    <div id="snoutiq-results"></div>
    <?php

    if (isset($_POST['snoutiq_submit'])) {
        snoutiq_process_submission();
    }

    return ob_get_clean();
}

function snoutiq_process_submission() {
    // Verify nonce
    if (!wp_verify_nonce($_POST['snoutiq_nonce'], 'snoutiq_submit')) {
        return;
    }

    // Prepare data
    $petData = [
        'name' => sanitize_text_field($_POST['pet_name']),
        'species' => sanitize_text_field($_POST['species']),
        'query' => sanitize_textarea_field($_POST['symptoms'])
    ];

    // Call API
    $apiUrl = get_option('snoutiq_api_url', 'http://your-server-ip:5000/query');

    $response = wp_remote_post($apiUrl, [
        'body' => json_encode($petData),
        'headers' => ['Content-Type' => 'application/json'],
        'timeout' => 60
    ]);

    if (is_wp_error($response)) {
        echo '<p class="error">Connection failed: ' . $response->get_error_message() . '</p>';
        return;
    }

    $body = json_decode(wp_remote_retrieve_body($response), true);

    if ($body['success']) {
        $data = $body['data'];
        ?>
        <div class="snoutiq-results">
            <h3>Analysis for <?php echo esc_html($data['pet_name']); ?></h3>
            <p><strong>Urgency:</strong> <?php echo esc_html(strtoupper($data['urgency_level'])); ?></p>
            <p><?php echo esc_html($data['summary']); ?></p>
        </div>
        <?php
    } else {
        echo '<p class="error">' . esc_html($body['error']) . '</p>';
    }
}

// Usage: Add [snoutiq_form] shortcode to any page/post
?>
```

### Example 2: Laravel Integration

```php
<?php
// app/Services/SnoutiqService.php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class SnoutiqService
{
    protected $apiUrl;

    public function __construct()
    {
        $this->apiUrl = config('services.snoutiq.url');
    }

    public function analyzeSymptoms(array $petData)
    {
        try {
            $response = Http::timeout(60)
                ->withHeaders(['Content-Type' => 'application/json'])
                ->post($this->apiUrl . '/query', $petData);

            if ($response->successful()) {
                return $response->json();
            }

            return [
                'success' => false,
                'error' => 'API request failed with status: ' . $response->status()
            ];

        } catch (\Exception $e) {
            return [
                'success' => false,
                'error' => 'Connection failed: ' . $e->getMessage()
            ];
        }
    }

    public function checkHealth()
    {
        try {
            $response = Http::timeout(10)->get($this->apiUrl . '/health');
            return $response->successful() ? $response->json() : null;
        } catch (\Exception $e) {
            return null;
        }
    }
}

// config/services.php
return [
    'snoutiq' => [
        'url' => env('SNOUTIQ_API_URL', 'http://your-server-ip:5000'),
    ],
];

// app/Http/Controllers/SymptomController.php
use App\Services\SnoutiqService;

class SymptomController extends Controller
{
    protected $snoutiq;

    public function __construct(SnoutiqService $snoutiq)
    {
        $this->snoutiq = $snoutiq;
    }

    public function analyze(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string',
            'species' => 'required|in:Dog,Cat',
            'query' => 'required|string|min:10'
        ]);

        $result = $this->snoutiq->analyzeSymptoms($validated);

        if ($result['success']) {
            return view('symptom.result', ['data' => $result['data']]);
        }

        return back()->withErrors(['error' => $result['error']]);
    }
}
```

### Example 3: AJAX with jQuery

```javascript
// Include this in your HTML page
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

<script>
$(document).ready(function() {
    $('#symptom-form').on('submit', function(e) {
        e.preventDefault();

        // Show loading
        $('#results').html('<p>Analyzing symptoms...</p>');
        $('#submit-btn').prop('disabled', true);

        // Prepare data
        var formData = {
            name: $('#pet-name').val(),
            species: $('#species').val(),
            breed: $('#breed').val() || 'Mixed',
            age: $('#age').val() || 'Unknown',
            weight: $('#weight').val() || 'Unknown',
            sex: $('#sex').val() || 'Unknown',
            vaccination_summary: $('#vaccination').val() || 'Not provided',
            medical_history: $('#history').val() || 'Not provided',
            query: $('#symptoms').val()
        };

        // Call API
        $.ajax({
            url: 'http://your-server-ip:5000/query',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            timeout: 60000,
            success: function(response) {
                if (response.success) {
                    displayResults(response.data);
                } else {
                    $('#results').html('<p class="error">Error: ' + response.error + '</p>');
                }
                $('#submit-btn').prop('disabled', false);
            },
            error: function(xhr, status, error) {
                $('#results').html('<p class="error">Failed to connect: ' + error + '</p>');
                $('#submit-btn').prop('disabled', false);
            }
        });
    });

    function displayResults(data) {
        var html = '<div class="analysis-results">';
        html += '<h3>Analysis for ' + data.pet_name + '</h3>';

        // Urgency badge
        var urgencyClass = 'urgency-' + data.urgency_level;
        html += '<span class="urgency-badge ' + urgencyClass + '">';
        html += data.urgency_level.toUpperCase();
        html += '</span>';

        // Summary
        html += '<p><strong>Summary:</strong> ' + data.summary + '</p>';

        // What we found
        html += '<p><strong>What We Found:</strong> ' + data.what_we_found + '</p>';

        // Immediate steps
        html += '<h4>What to Do Now:</h4><ul>';
        data.immediate_steps.forEach(function(step) {
            html += '<li>' + step + '</li>';
        });
        html += '</ul>';

        // Home care
        html += '<h4>Home Care Tips:</h4><ul>';
        data.home_care_tips.forEach(function(tip) {
            html += '<li>' + tip + '</li>';
        });
        html += '</ul>';

        // When to see vet
        html += '<p><strong>See Vet If:</strong> ' + data.when_to_see_vet + '</p>';

        // Service recommendation
        var service = data.service_recommendation.replace('_', ' ').toUpperCase();
        html += '<p><strong>Recommended:</strong> ' + service + '</p>';

        html += '</div>';

        $('#results').html(html);
    }
});
</script>

<style>
.urgency-badge {
    display: inline-block;
    padding: 5px 15px;
    border-radius: 20px;
    color: white;
    font-weight: bold;
    margin: 10px 0;
}
.urgency-emergency { background: #e74c3c; }
.urgency-urgent { background: #f39c12; }
.urgency-routine { background: #27ae60; }
.error { color: #e74c3c; }
</style>
```

---

## 🔧 Configuration

### API URL Configuration

```php
<?php
// config.php

define('SNOUTIQ_API_BASE', 'http://your-server-ip:5000');
define('SNOUTIQ_TIMEOUT', 60);

// For production with domain
// define('SNOUTIQ_API_BASE', 'https://api.yourdomain.com');
?>
```

### Using .env File (Laravel, Symfony, etc.)

```env
# .env file
SNOUTIQ_API_URL=http://your-server-ip:5000
SNOUTIQ_TIMEOUT=60
```

```php
// Usage
$apiUrl = getenv('SNOUTIQ_API_URL');
```

---

## 🛡️ Error Handling

### Comprehensive Error Handling

```php
<?php
function callSnoutiqAPI($petData, $apiUrl) {
    // Step 1: Validate input
    $errors = [];

    if (empty($petData['name'])) {
        $errors[] = 'Pet name is required';
    }

    if (empty($petData['species']) || !in_array($petData['species'], ['Dog', 'Cat'])) {
        $errors[] = 'Valid species (Dog/Cat) is required';
    }

    if (empty($petData['query']) || strlen($petData['query']) < 10) {
        $errors[] = 'Symptom description must be at least 10 characters';
    }

    if (!empty($errors)) {
        return [
            'success' => false,
            'error' => implode(', ', $errors)
        ];
    }

    // Step 2: Check if cURL is available
    if (!function_exists('curl_init')) {
        return [
            'success' => false,
            'error' => 'cURL extension not installed'
        ];
    }

    // Step 3: Make API call
    $ch = curl_init($apiUrl);

    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($petData),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_TIMEOUT => 60,
        CURLOPT_CONNECTTIMEOUT => 10
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curlError = curl_error($ch);
    curl_close($ch);

    // Step 4: Handle connection errors
    if ($curlError) {
        return [
            'success' => false,
            'error' => 'Connection failed: ' . $curlError
        ];
    }

    // Step 5: Handle HTTP errors
    if ($httpCode !== 200) {
        return [
            'success' => false,
            'error' => 'API returned error (HTTP ' . $httpCode . ')'
        ];
    }

    // Step 6: Parse JSON
    $result = json_decode($response, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        return [
            'success' => false,
            'error' => 'Invalid response from API'
        ];
    }

    // Step 7: Return result
    return $result;
}

// Usage with error handling
$result = callSnoutiqAPI($petData, $apiUrl);

if (!$result['success']) {
    // Log error
    error_log('SNOUTIQ API Error: ' . $result['error']);

    // Show user-friendly message
    echo '<p class="error">Unable to analyze symptoms. Please try again later.</p>';
} else {
    // Display results
    $data = $result['data'];
    // ...
}
?>
```

---

## 🎨 Response Display Templates

### Simple HTML Template

```php
<?php
function displayAnalysis($data) {
    ?>
    <div class="snoutiq-analysis">
        <div class="header">
            <h2>Analysis for <?php echo htmlspecialchars($data['pet_name']); ?></h2>
            <span class="urgency-<?php echo $data['urgency_level']; ?>">
                <?php echo strtoupper($data['urgency_level']); ?>
            </span>
        </div>

        <div class="summary">
            <h3>Summary</h3>
            <p><?php echo htmlspecialchars($data['summary']); ?></p>
        </div>

        <div class="findings">
            <h3>What We Found</h3>
            <p><?php echo htmlspecialchars($data['what_we_found']); ?></p>
        </div>

        <div class="immediate-steps">
            <h3>What to Do Now</h3>
            <ul>
                <?php foreach ($data['immediate_steps'] as $step): ?>
                    <li><?php echo htmlspecialchars($step); ?></li>
                <?php endforeach; ?>
            </ul>
        </div>

        <div class="home-care">
            <h3>Home Care Tips</h3>
            <ul>
                <?php foreach ($data['home_care_tips'] as $tip): ?>
                    <li><?php echo htmlspecialchars($tip); ?></li>
                <?php endforeach; ?>
            </ul>
        </div>

        <div class="vet-advice">
            <h3>When to See a Veterinarian</h3>
            <p><?php echo htmlspecialchars($data['when_to_see_vet']); ?></p>
        </div>

        <div class="recommendation">
            <p><strong>Recommended Service:</strong>
                <?php echo str_replace('_', ' ', strtoupper($data['service_recommendation'])); ?>
            </p>
            <p><strong>Confidence:</strong>
                <?php echo ucfirst($data['confidence']); ?>
            </p>
        </div>

        <?php if (!empty($data['additional_notes'])): ?>
        <div class="additional-notes">
            <h3>Additional Notes</h3>
            <p><?php echo htmlspecialchars($data['additional_notes']); ?></p>
        </div>
        <?php endif; ?>

        <div class="disclaimer">
            <p><em>⚠️ This is an AI-powered advisory tool. Always consult a licensed veterinarian for professional diagnosis.</em></p>
        </div>
    </div>

    <style>
    .snoutiq-analysis {
        max-width: 800px;
        margin: 20px auto;
        padding: 20px;
        background: #fff;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .header {
        border-bottom: 2px solid #eee;
        padding-bottom: 15px;
        margin-bottom: 20px;
    }
    .urgency-emergency {
        background: #e74c3c;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    .urgency-urgent {
        background: #f39c12;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    .urgency-routine {
        background: #27ae60;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    .snoutiq-analysis h3 {
        color: #2c3e50;
        margin-top: 20px;
    }
    .snoutiq-analysis ul {
        list-style: none;
        padding: 0;
    }
    .snoutiq-analysis li {
        padding: 10px;
        margin: 5px 0;
        background: #f8f9fa;
        border-left: 3px solid #3498db;
        border-radius: 3px;
    }
    .disclaimer {
        margin-top: 20px;
        padding: 15px;
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 5px;
    }
    </style>
    <?php
}
?>
```

---

## 📧 Email Notification Integration

```php
<?php
function sendAnalysisEmail($data, $userEmail) {
    $subject = "SNOUTIQ Analysis for " . $data['pet_name'];

    $message = "
    <html>
    <body>
        <h2>Pet Symptom Analysis</h2>
        <p><strong>Pet Name:</strong> {$data['pet_name']}</p>
        <p><strong>Urgency:</strong> {$data['urgency_level']}</p>

        <h3>Summary</h3>
        <p>{$data['summary']}</p>

        <h3>Immediate Steps</h3>
        <ul>
    ";

    foreach ($data['immediate_steps'] as $step) {
        $message .= "<li>$step</li>";
    }

    $message .= "
        </ul>

        <h3>When to See Vet</h3>
        <p>{$data['when_to_see_vet']}</p>

        <p><em>This is an AI-powered advisory. Please consult a veterinarian.</em></p>
    </body>
    </html>
    ";

    $headers = [
        'MIME-Version: 1.0',
        'Content-type: text/html; charset=UTF-8',
        'From: SNOUTIQ <noreply@yourdomain.com>'
    ];

    mail($userEmail, $subject, $message, implode("\r\n", $headers));
}
?>
```

---

## 🔍 Testing Your Integration

### Test Script

```php
<?php
// test_snoutiq.php

require_once 'snoutiq_api.php';

// Test data
$testData = [
    'name' => 'Test Dog',
    'species' => 'Dog',
    'breed' => 'Labrador',
    'age' => '5 years',
    'weight' => '30 kg',
    'sex' => 'Male',
    'vaccination_summary' => 'Up to date',
    'medical_history' => 'No major issues',
    'query' => 'My dog has been vomiting since this morning and seems very weak'
];

echo "Testing SNOUTIQ API...\n\n";

// Test health endpoint first
$healthUrl = 'http://your-server-ip:5000/health';
$ch = curl_init($healthUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

echo "Health Check:\n";
echo $response . "\n\n";

// Test main query endpoint
echo "Testing symptom analysis...\n";
$result = analyzeSymptoms($testData, 'http://your-server-ip:5000/query');

if ($result['success']) {
    echo "✅ SUCCESS!\n\n";
    echo "Pet: " . $result['data']['pet_name'] . "\n";
    echo "Urgency: " . $result['data']['urgency_level'] . "\n";
    echo "Summary: " . $result['data']['summary'] . "\n";
} else {
    echo "❌ FAILED!\n";
    echo "Error: " . $result['error'] . "\n";
}
?>
```

Run test:
```bash
php test_snoutiq.php
```

---

## 📚 Common Issues & Solutions

### Issue 1: "Connection failed"

**Cause**: Backend server not reachable

**Solutions:**
```php
// Check if server is running
$ch = curl_init('http://your-server-ip:5000/health');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 5);
$response = curl_exec($ch);

if (curl_error($ch)) {
    echo "Server is not reachable: " . curl_error($ch);
} else {
    echo "Server is up: " . $response;
}
curl_close($ch);
```

### Issue 2: "cURL extension not installed"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install php-curl
sudo systemctl restart apache2

# CentOS
sudo yum install php-curl
sudo systemctl restart httpd
```

### Issue 3: Timeout errors

**Solution:**
```php
// Increase timeout
curl_setopt($ch, CURLOPT_TIMEOUT, 120);  // 2 minutes
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);  // 30 seconds to connect
```

### Issue 4: JSON parsing errors

**Solution:**
```php
$result = json_decode($response, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    echo "JSON Error: " . json_last_error_msg();
    echo "Response: " . $response;
}
```

---

## ✅ Integration Checklist

- [ ] API URL configured correctly
- [ ] cURL extension installed in PHP
- [ ] Test health endpoint (`/health`) works
- [ ] Test query endpoint (`/query`) with sample data
- [ ] Error handling implemented
- [ ] Timeout configured (60+ seconds)
- [ ] Input validation working
- [ ] Results display looks good
- [ ] Mobile-responsive design
- [ ] Email notifications (if needed)
- [ ] Logging for debugging
- [ ] Production URL updated (not localhost)

---

**🎉 You're ready to integrate SNOUTIQ!**

For any issues, check the DEPLOYMENT_GUIDE.md or TECHNICAL_DOCUMENTATION.md files.

---

*PHP Integration Guide Version 1.0*
