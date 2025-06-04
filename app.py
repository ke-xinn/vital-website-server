from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('vital_signs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vital_signs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            temperature REAL,
            spo2 INTEGER,
            bpm INTEGER,
            sys INTEGER,
            dia INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Store latest readings in memory for real-time updates
latest_data = {
    'device_id': '',
    'temperature': 0,
    'spo2': 0,
    'bpm': 0,
    'sys': 0,
    'dia': 0,
    'timestamp': '',
    'status': 'No data received'
}

def get_health_status(temp, spo2, bpm, sys, dia):
    """Determine health status based on vital signs"""
    alerts = []
    
    # Temperature alerts
    if temp < 35.0:
        alerts.append("Hypothermia")
    elif temp > 37.5:
        alerts.append("Hyperthermia")
    
    # SpO2 alerts
    if spo2 < 95:
        alerts.append("Low SpO2")
    
    # Blood pressure alerts
    if sys < 80 or dia < 60:
        alerts.append("Hypotension")
    elif sys >= 180 or dia >= 120:
        alerts.append("Emergency - Hypertensive Crisis")
    elif sys >= 140 or dia >= 90:
        alerts.append("Hypertension")
    elif sys >= 130 or dia >= 80:
        alerts.append("Prehypertension")
    
    # Heart rate alerts
    if bpm <= 60:
        alerts.append("Bradycardia")
    elif bpm >= 100:
        alerts.append("Tachycardia")
    
    if not alerts:
        return "Normal"
    else:
        return " | ".join(alerts)

@app.route('/')
def dashboard():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_data():
    """Receive data from ESP32"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        
        # Extract data
        device_id = data.get('device_id', 'Unknown')
        temperature = float(data.get('temperature', 0))
        spo2 = int(data.get('spo2', 0))
        bpm = int(data.get('bpm', 0))
        sys = int(data.get('sys', 0))
        dia = int(data.get('dia', 0))
        
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Store in database
        conn = sqlite3.connect('vital_signs.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vital_signs (device_id, temperature, spo2, bpm, sys, dia, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (device_id, temperature, spo2, bpm, sys, dia, timestamp))
        conn.commit()
        conn.close()
        
        # Update latest data
        health_status = get_health_status(temperature, spo2, bpm, sys, dia)
        latest_data.update({
            'device_id': device_id,
            'temperature': temperature,
            'spo2': spo2,
            'bpm': bpm,
            'sys': sys,
            'dia': dia,
            'timestamp': timestamp,
            'status': health_status
        })
        
        print(f"Data received from {device_id}: Temp={temperature}°C, SpO2={spo2}%, HR={bpm}bpm, BP={sys}/{dia}mmHg")
        
        return jsonify({
            'message': 'Data received successfully',
            'status': health_status,
            'timestamp': timestamp
        }), 200
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/latest')
def get_latest_data():
    """Get the latest vital signs data"""
    return jsonify(latest_data)

@app.route('/api/history')
def get_history():
    """Get historical data"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        conn = sqlite3.connect('vital_signs.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT device_id, temperature, spo2, bpm, sys, dia, timestamp
            FROM vital_signs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'device_id': row[0],
                'temperature': row[1],
                'spo2': row[2],
                'bpm': row[3],
                'sys': row[4],
                'dia': row[5],
                'timestamp': row[6]
            })
        
        return jsonify(history)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get basic statistics"""
    try:
        conn = sqlite3.connect('vital_signs.db')
        cursor = conn.cursor()
        
        # Get averages for last 24 hours
        cursor.execute('''
            SELECT 
                AVG(temperature) as avg_temp,
                AVG(spo2) as avg_spo2,
                AVG(bpm) as avg_bpm,
                AVG(sys) as avg_sys,
                AVG(dia) as avg_dia,
                COUNT(*) as total_readings
            FROM vital_signs
            WHERE timestamp >= datetime('now', '-24 hours')
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[5] > 0:  # Check if we have readings
            stats = {
                'avg_temperature': round(row[0], 1) if row[0] else 0,
                'avg_spo2': round(row[1], 1) if row[1] else 0,
                'avg_bpm': round(row[2], 1) if row[2] else 0,
                'avg_sys': round(row[3], 1) if row[3] else 0,
                'avg_dia': round(row[4], 1) if row[4] else 0,
                'total_readings': row[5]
            }
        else:
            stats = {
                'avg_temperature': 0,
                'avg_spo2': 0,
                'avg_bpm': 0,
                'avg_sys': 0,
                'avg_dia': 0,
                'total_readings': 0
            }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    print("Starting 4Vita Health Dashboard Server...")
    print("Dashboard will be available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)