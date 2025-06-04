from flask import Flask, request, jsonify, render_template
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Simple in-memory storage
data_store = []

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_data():
    """Simplified upload endpoint for debugging"""
    logger.info("Upload endpoint called")
    
    try:
        # Log everything about the request
        logger.info(f"Method: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Raw data: {request.get_data()}")
        
        # Try to get JSON data
        if request.is_json:
            data = request.get_json()
            logger.info(f"JSON data received: {data}")
        else:
            logger.error("Request is not JSON")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        if not data:
            logger.error("No data in request")
            return jsonify({"error": "No JSON data received"}), 400
        
        # Store the data with timestamp
        stored_data = {
            **data,
            'server_timestamp': datetime.now().isoformat()
        }
        data_store.append(stored_data)
        
        # Keep only last 50 items
        if len(data_store) > 50:
            data_store.pop(0)
        
        logger.info(f"Data stored successfully: {stored_data}")
        
        return jsonify({
            "success": True,
            "message": "Data received successfully",
            "data": stored_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in upload: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/latest', methods=['GET'])
def get_latest():
    """Get latest data - FIXED VERSION"""
    try:
        logger.info(f"Latest data request - data_store has {len(data_store)} items")
        
        if not data_store:
            logger.info("No data available in store")
            return jsonify({
                "message": "No data available",
                "bpm": None,
                "sys": None,
                "dia": None,
                "temperature": None,
                "spo2": None,
                "timestamp": None,
                "status": "No data received"
            }), 200
        
        latest = data_store[-1]  # Get last item
        logger.info(f"Returning latest data: {latest}")
        return jsonify(latest), 200
        
    except Exception as e:
        logger.error(f"Error getting latest: {e}")
        return jsonify({"error": str(e)}), 500

# REMOVED THE DUPLICATE ROUTE - this was causing the conflict!

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get data history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        history = data_store[-limit:] if len(data_store) > limit else data_store
        history.reverse()  # Most recent first
        logger.info(f"Returning {len(history)} history items")
        return jsonify(history), 200
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check server status"""
    return jsonify({
        "status": "Server running",
        "timestamp": datetime.now().isoformat(),
        "data_count": len(data_store),
        "latest_data": data_store[-1] if data_store else None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)