"""
SNOUTIQ RAG System - Core Module
Veterinary symptom checker using RAG (Retrieval-Augmented Generation)
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from typing import Dict, List, Any
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-2.0-flash"

# Search parameters
TOP_K = 10
MIN_SIMILARITY = 0.3
SEVERITY_BOOST = {"emergency": 1.5, "urgent": 1.2, "routine": 1.0}

# Medical synonyms for query expansion
MEDICAL_SYNONYMS = {
    'vomit': ['vomiting', 'throwing up', 'emesis'],
    'diarrhea': ['loose stool', 'loose motion', 'watery stool'],
    'pee': ['urinate', 'urine', 'urination'],
    'poop': ['stool', 'feces', 'defecate'],
    'cough': ['coughing', 'hacking'],
    'scratch': ['scratching', 'itching', 'itchy'],
    'limp': ['limping', 'lame', 'not walking'],
    'breath': ['breathing', 'respiratory', 'panting'],
    'eat': ['eating', 'appetite', 'food'],
    'blood': ['bleeding', 'bloody'],
}

# Emergency keywords
EMERGENCY_KEYWORDS = [
    'bleeding', 'blood', 'seizure', 'unconscious', 'not breathing',
    'collapsed', 'severe pain', 'bloat', 'poisoning', 'trauma',
    'snake bite', 'broken bone', 'can\'t stand', 'blue gums'
]


class SnoutiqRAG:
    """SNOUTIQ RAG System for veterinary symptom analysis"""

    def __init__(self, api_key: str):
        """Initialize the RAG system with API key"""
        logger.info("📊 Loading AI models...")

        # Load embedding model
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)

        # Configure Gemini
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel(GEMINI_MODEL)

        self.documents = []
        self.metadata = []
        self.index = None
        self.loaded = False

        logger.info("✅ Models loaded successfully")

    def load_datasets(self, dataset_files: List[str]) -> bool:
        """Load all dataset files and create embeddings"""
        logger.info("📚 Loading veterinary datasets...")

        all_texts = []
        all_metadata = []

        for filename in dataset_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                category = filename.replace('master_', '').replace('_dataset.json', '').split('/')[-1]
                entries = data.get('entries', data if isinstance(data, list) else [])

                for entry in entries:
                    # Combine symptom and description for embedding
                    text = f"{entry.get('symptom', '')}. {entry.get('description', '')}"
                    all_texts.append(text)

                    # Store metadata
                    entry['category'] = category
                    all_metadata.append(entry)

                logger.info(f"   ✓ {category}: {len(entries)} entries")

            except Exception as e:
                logger.warning(f"   ⚠ Skipping {filename}: {e}")
                continue

        if not all_texts:
            logger.error("❌ No data loaded!")
            return False

        # Create embeddings
        logger.info(f"🔄 Creating embeddings for {len(all_texts)} entries...")
        embeddings = self.embedder.encode(
            all_texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        self.index.add(embeddings.astype('float32'))

        self.documents = all_texts
        self.metadata = all_metadata
        self.loaded = True

        logger.info(f"✅ System ready with {len(all_texts)} entries!")
        return True

    def expand_query(self, query: str) -> str:
        """Expand query with medical synonyms"""
        query_lower = query.lower()
        expanded = [query]

        for term, synonyms in MEDICAL_SYNONYMS.items():
            if term in query_lower:
                for syn in synonyms[:2]:
                    if syn not in query_lower:
                        expanded.append(query_lower.replace(term, syn))

        return ' '.join(expanded[:3])  # Limit to 3 variations

    def detect_emergency(self, query: str) -> bool:
        """Detect if query indicates emergency"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in EMERGENCY_KEYWORDS)

    def search(self, query: str, species: str = None, top_k: int = TOP_K) -> List[Dict]:
        """Search for relevant entries"""
        if not self.loaded:
            return []

        # Expand query
        expanded_query = self.expand_query(query)

        # Get query embedding
        query_emb = self.embedder.encode([expanded_query], normalize_embeddings=True)

        # Search
        scores, indices = self.index.search(
            query_emb.astype('float32'),
            min(top_k * 2, len(self.documents))
        )

        # Process results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score < MIN_SIMILARITY:
                continue

            meta = self.metadata[idx]

            # Species filter
            if species and meta.get('species', '').lower() != species.lower():
                continue

            # Apply severity boost
            severity = meta.get('severity', 'routine')
            boosted_score = float(score) * SEVERITY_BOOST.get(severity, 1.0)

            results.append({
                'score': boosted_score,
                'metadata': meta,
                'text': self.documents[idx]
            })

        # Sort by boosted score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def generate_response(
        self,
        pet_details: Dict[str, Any],
        query: str,
        matched_entries: List[Dict]
    ) -> Dict[str, Any]:
        """Generate structured response with pet details"""

        # Build context from matched entries
        context_parts = []
        for i, entry in enumerate(matched_entries[:3], 1):
            meta = entry['metadata']
            context_parts.append(f"""
Match {i}:
  Symptom: {meta.get('symptom', 'N/A')}
  Description: {meta.get('description', 'N/A')}
  Severity: {meta.get('severity', 'N/A')}
  Home Care: {meta.get('home_care_india', 'N/A')}
  When to See Vet: {meta.get('vet_triggers', 'N/A')}
""")

        context = '\n'.join(context_parts)

        # Build pet details summary
        pet_summary = f"""
Pet Name: {pet_details.get('name', 'Not provided')}
Species: {pet_details.get('species', 'Not provided')}
Breed: {pet_details.get('breed', 'Not provided')}
Age: {pet_details.get('age', 'Not provided')}
Weight: {pet_details.get('weight', 'Not provided')}
Sex: {pet_details.get('sex', 'Not provided')}
Vaccination Status: {pet_details.get('vaccination_summary', 'Not provided')}
Medical History: {pet_details.get('medical_history', 'Not provided')}
"""

        # Detect emergency
        is_emergency = self.detect_emergency(query)

        # Create prompt
        prompt = f"""
You are a veterinary AI assistant for SNOUTIQ, a pet health platform in India.

PET DETAILS:
{pet_summary}

PET PARENT'S QUERY:
{query}

RELEVANT MEDICAL INFORMATION:
{context}

EMERGENCY STATUS: {'⚠️ YES - URGENT ATTENTION NEEDED' if is_emergency else 'No immediate emergency detected'}

INSTRUCTIONS:
Generate a response for the pet parent in this EXACT JSON format:

{{
  "pet_name": "{pet_details.get('name', 'Your pet')}",
  "summary": "Brief 1-2 sentence summary of the situation",
  "what_we_found": "Detailed explanation based on symptoms and pet's medical history (3-4 sentences)",
  "immediate_steps": [
    "Step 1: What to do right now",
    "Step 2: How to monitor",
    "Step 3: What to avoid"
  ],
  "home_care_tips": [
    "Tip 1: Specific care advice for India",
    "Tip 2: What to watch for",
    "Tip 3: How to make pet comfortable"
  ],
  "when_to_see_vet": "Clear criteria for when veterinary care is needed",
  "urgency_level": "emergency/urgent/routine",
  "service_recommendation": "in_clinic/video_consult",
  "confidence": "high/medium/low",
  "additional_notes": "Any breed-specific, age-specific, or climate considerations for India"
}}

IMPORTANT:
- Use simple, empathetic language for pet parents
- Consider India's hot/humid climate
- Consider pet's age, breed, and medical history
- If emergency, stress immediate vet visit
- Return ONLY valid JSON, no extra text
"""

        try:
            # Generate response
            response = self.llm.generate_content(prompt)

            # Extract JSON
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)

            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                result = self._create_fallback_response(pet_details, matched_entries, is_emergency)

            # Add metadata
            result['query_metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'num_matches': len(matched_entries),
                'is_emergency': is_emergency,
                'top_match_score': matched_entries[0]['score'] if matched_entries else 0
            }

            return result

        except Exception as e:
            logger.error(f"⚠️ LLM Error: {e}")
            return self._create_fallback_response(pet_details, matched_entries, is_emergency)

    def _create_fallback_response(
        self,
        pet_details: Dict,
        matched_entries: List[Dict],
        is_emergency: bool
    ) -> Dict:
        """Fallback response when LLM fails"""
        if not matched_entries:
            return {
                "pet_name": pet_details.get('name', 'Your pet'),
                "summary": "We couldn't find specific information for these symptoms.",
                "what_we_found": "The symptoms you described don't closely match our database. This doesn't mean it's not serious.",
                "immediate_steps": [
                    "Monitor your pet closely",
                    "Note any changes in behavior or symptoms",
                    "Keep your pet comfortable"
                ],
                "home_care_tips": [
                    "Ensure fresh water is available",
                    "Keep in a cool, comfortable place",
                    "Don't force food if not eating"
                ],
                "when_to_see_vet": "Given the uncertainty, we recommend consulting a veterinarian soon.",
                "urgency_level": "urgent" if is_emergency else "routine",
                "service_recommendation": "in_clinic" if is_emergency else "video_consult",
                "confidence": "low",
                "additional_notes": "Without clear symptom matches, professional veterinary assessment is recommended."
            }

        # Use top match
        top = matched_entries[0]['metadata']

        return {
            "pet_name": pet_details.get('name', 'Your pet'),
            "summary": f"Based on symptoms, this appears to be related to {top.get('symptom', 'the condition')}",
            "what_we_found": top.get('description', ''),
            "immediate_steps": [
                "Follow home care guidelines below",
                "Monitor symptoms closely",
                "Note any worsening"
            ],
            "home_care_tips": [top.get('home_care_india', 'Keep comfortable and monitor')],
            "when_to_see_vet": top.get('vet_triggers', 'If symptoms persist or worsen'),
            "urgency_level": top.get('severity', 'routine'),
            "service_recommendation": top.get('service_recommendation', 'video_consult'),
            "confidence": "medium",
            "additional_notes": top.get('indian_climate_factors', '')
        }

    def process_query(
        self,
        pet_details: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """Main function: Process pet details + query → Return response"""

        # Extract species for filtering
        species = pet_details.get('species', '').lower()
        if 'dog' in species:
            species = 'dogs'
        elif 'cat' in species:
            species = 'cats'
        else:
            species = None

        # Search
        logger.info(f"🔍 Searching for: {query[:50]}...")
        matches = self.search(query, species=species)
        logger.info(f"   Found {len(matches)} relevant entries")

        # Generate response
        logger.info(f"💬 Generating response...")
        response = self.generate_response(pet_details, query, matches)
        logger.info(f"   ✅ Response ready")

        return response
