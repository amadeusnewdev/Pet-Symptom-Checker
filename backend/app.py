"""
SNOUTIQ Flask API
Production-ready veterinary symptom checker API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_system import SnoutiqRAG
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any
import glob

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Global RAG system instance
rag_system = None


def validate_pet_details(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate pet details from request"""
    required_fields = ['name', 'species', 'query']

    for field in required_fields:
        if field not in data or not data[field].strip():
            return False, f"Missing required field: {field}"

    # Validate species
    species = data['species'].lower()
    if 'dog' not in species and 'cat' not in species:
        return False, "Species must be 'Dog' or 'Cat'"

    # Validate query length
    if len(data['query']) < 10:
        return False, "Query must be at least 10 characters long"

    if len(data['query']) > 1000:
        return False, "Query must be less than 1000 characters"

    return True, ""


def initialize_rag_system():
    """Initialize the RAG system with datasets"""
    global rag_system

    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    logger.info("🚀 Initializing SNOUTIQ RAG System...")

    # Create RAG instance
    rag_system = SnoutiqRAG(api_key=api_key)

    # Load datasets
    dataset_path = os.path.join(os.path.dirname(__file__), 'datasets')
    dataset_files = glob.glob(os.path.join(dataset_path, 'master_*_dataset.json'))

    if not dataset_files:
        raise FileNotFoundError(f"No dataset files found in {dataset_path}")

    logger.info(f"Found {len(dataset_files)} dataset files")

    success = rag_system.load_datasets(dataset_files)

    if not success:
        raise RuntimeError("Failed to load datasets")

    logger.info("✅ RAG System initialized successfully")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'SNOUTIQ API',
        'rag_loaded': rag_system is not None and rag_system.loaded
    }), 200


@app.route('/query', methods=['POST'])
def process_query():
    """
    Main endpoint: Process pet symptom query

    Request body:
    {
        "name": "Pet name",
        "species": "Dog/Cat",
        "breed": "Breed (optional)",
        "age": "Age (optional)",
        "weight": "Weight (optional)",
        "sex": "Male/Female (optional)",
        "vaccination_summary": "Vaccination status (optional)",
        "medical_history": "Medical history (optional)",
        "query": "Symptom description"
    }

    Response:
    {
        "success": true,
        "data": { ... response object ... }
    }
    """
    try:
        # Check if RAG system is initialized
        if rag_system is None or not rag_system.loaded:
            return jsonify({
                'success': False,
                'error': 'RAG system not initialized'
            }), 503

        # Get request data
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        # Validate required fields
        is_valid, error_msg = validate_pet_details(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400

        # Build pet details
        pet_details = {
            'name': data['name'].strip(),
            'species': data['species'].strip(),
            'breed': data.get('breed', 'Mixed').strip(),
            'age': data.get('age', 'Unknown').strip(),
            'weight': data.get('weight', 'Unknown').strip(),
            'sex': data.get('sex', 'Unknown').strip(),
            'vaccination_summary': data.get('vaccination_summary', 'Not provided').strip(),
            'medical_history': data.get('medical_history', 'No history provided').strip()
        }

        query = data['query'].strip()

        # Log request
        logger.info(f"Processing query for {pet_details['name']} ({pet_details['species']})")

        # Process query
        response = rag_system.process_query(pet_details, query)

        # Return response
        return jsonify({
            'success': True,
            'data': response
        }), 200

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/datasets/info', methods=['GET'])
def dataset_info():
    """Get information about loaded datasets"""
    if rag_system is None or not rag_system.loaded:
        return jsonify({
            'success': False,
            'error': 'RAG system not initialized'
        }), 503

    return jsonify({
        'success': True,
        'data': {
            'total_entries': len(rag_system.documents),
            'embedding_model': 'all-MiniLM-L6-v2',
            'llm_model': 'gemini-2.0-flash'
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    try:
        # Initialize RAG system on startup
        initialize_rag_system()

        # Start Flask server
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_ENV') == 'development'

        logger.info(f"🚀 Starting SNOUTIQ API on port {port}")
        app.run(host='0.0.0.0', port=port, debug=debug)

    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        exit(1)
