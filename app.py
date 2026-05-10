"""
Responsible AI Gateway - Flask Backend
A secure API gateway for AI interactions with built-in PII filtering,
audit logging, and GDPR compliance for Dutch public sector use.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, Tuple
from contextlib import contextmanager

from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS

from src.validator import PIIValidator
from src.ai_service import AIService


app = Flask(__name__)
CORS(app)

# Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'audit_logs.db')
STRICT_MODE = os.getenv('STRICT_MODE', 'true').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Optional - falls back to mock if not set
AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')  # Cost-effective default


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_database_directory()
        self._init_database()

    def log_request(
        self,
        input_length: int,
        pii_detected: bool,
        violations_count: int,
        status_code: int,
        processing_time_ms: float,
        client_ip: str = None,
        user_agent: str = None
    ) -> int:
        """
        Log a request to the audit database.

        Returns:
            The ID of the inserted log entry
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO request_logs
                (timestamp, input_length, pii_detected, violations_count,
                 status_code, processing_time_ms, client_ip, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.utcnow().isoformat(),
                input_length,
                pii_detected,
                violations_count,
                status_code,
                processing_time_ms,
                client_ip,
                user_agent
            ))
            conn.commit()
            return cursor.lastrowid

    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit statistics for monitoring."""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN pii_detected = 1 THEN 1 ELSE 0 END) as blocked_requests,
                    AVG(processing_time_ms) as avg_processing_time,
                    SUM(violations_count) as total_violations
                FROM request_logs
            ''')
            row = cursor.fetchone()

            return {
                "total_requests": row[0] or 0,
                "blocked_requests": row[1] or 0,
                "avg_processing_time_ms": round(row[2] or 0, 2),
                "total_violations": row[3] or 0
            }

    def _ensure_database_directory(self) -> None:
        """Ensure the directory for the database file exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def _init_database(self) -> None:
        """Initialize the database schema."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    input_length INTEGER NOT NULL,
                    pii_detected BOOLEAN NOT NULL,
                    violations_count INTEGER NOT NULL,
                    status_code INTEGER NOT NULL,
                    processing_time_ms REAL,
                    client_ip TEXT,
                    user_agent TEXT
                )
            ''')
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()


# Initialize components
db_manager = DatabaseManager(DATABASE_PATH)
pii_validator = PIIValidator(strict_mode=STRICT_MODE)
ai_service = AIService(api_key=OPENAI_API_KEY, model=AI_MODEL)


@app.route('/')
def index() -> str:
    """Serve the main application page."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze() -> Tuple[Response, int]:
    """
    Main endpoint for AI analysis with PII filtering.

    Expected JSON input:
        {
            "text": "The user input to analyze"
        }

    Returns:
        JSON response with AI result and safety report
    """
    start_time = datetime.utcnow()

    try:
        # Parse request
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({
                "error": "Missing 'text' field in request body",
                "status": "error"
            }), 400

        user_input = data['text']

        if not isinstance(user_input, str):
            return jsonify({
                "error": "'text' must be a string",
                "status": "error"
            }), 400

        if not user_input.strip():
            return jsonify({
                "error": "Input text cannot be empty",
                "status": "error"
            }), 400

        if len(user_input) > 10000:
            return jsonify({
                "error": "Input text exceeds maximum length of 10,000 characters",
                "status": "error"
            }), 400

        # Step 1: PII Validation
        is_safe, detections, sanitized_text = pii_validator.validate(user_input)
        safety_report = pii_validator.get_safety_report(detections)

        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Log to audit database
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')

        # If PII detected, block the request
        if not is_safe:
            db_manager.log_request(
                input_length=len(user_input),
                pii_detected=True,
                violations_count=len(detections),
                status_code=403,
                processing_time_ms=processing_time,
                client_ip=client_ip,
                user_agent=user_agent
            )

            return jsonify({
                "status": "blocked",
                "message": "Persoonlijke gegevens gedetecteerd. Verzoek geblokkeerd ter bescherming van privacy.",
                "safety_report": safety_report,
                "timestamp": datetime.utcnow().isoformat()
            }), 403

        # Step 2: Process with AI (using sanitized text)
        try:
            ai_result = ai_service.analyze(sanitized_text)
        except Exception as ai_error:
            db_manager.log_request(
                input_length=len(user_input),
                pii_detected=False,
                violations_count=0,
                status_code=500,
                processing_time_ms=processing_time,
                client_ip=client_ip,
                user_agent=user_agent
            )

            return jsonify({
                "error": "AI processing failed",
                "status": "error",
                "details": str(ai_error)
            }), 500

        # Success - log and return
        db_manager.log_request(
            input_length=len(user_input),
            pii_detected=False,
            violations_count=0,
            status_code=200,
            processing_time_ms=processing_time,
            client_ip=client_ip,
            user_agent=user_agent
        )

        return jsonify({
            "status": "success",
            "result": ai_result,
            "safety_report": safety_report,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        # Catch-all error handler
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)

        return jsonify({
            "error": "Internal server error",
            "status": "error",
            "message": "Er is een onverwachte fout opgetreden"
        }), 500


@app.route('/health', methods=['GET'])
def health() -> Tuple[Response, int]:
    """Health check endpoint."""
    try:
        # Test database connection
        stats = db_manager.get_audit_stats()

        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "audit_stats": stats
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route('/stats', methods=['GET'])
def stats() -> Tuple[Response, int]:
    """Get audit statistics."""
    try:
        stats = db_manager.get_audit_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({
            "error": "Failed to retrieve statistics",
            "details": str(e)
        }), 500


@app.route('/ai-status', methods=['GET'])
def ai_status() -> Tuple[Response, int]:
    """Get AI service status and configuration."""
    try:
        service_info = ai_service.get_service_info()
        return jsonify(service_info), 200
    except Exception as e:
        return jsonify({
            "error": "Failed to retrieve AI service status",
            "details": str(e)
        }), 500


@app.errorhandler(404)
def not_found(e) -> Tuple[Response, int]:
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "status": "error"
    }), 404


@app.errorhandler(500)
def internal_error(e) -> Tuple[Response, int]:
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'

    print(f"Responsible AI Gateway starting on port {port}")
    print(f"Database: {DATABASE_PATH}")
    print(f"Strict Mode: {STRICT_MODE}")
    print(f"AI Model: {AI_MODEL}")
    print(f"API Key: {'[Configured]' if OPENAI_API_KEY else '[Not set - using mock]'}")
    print(f"Debug Mode: {debug}")

    app.run(host='0.0.0.0', port=port, debug=debug)
