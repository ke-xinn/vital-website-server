from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

latest_data = {}

@app.route('/')
def index():
    return render_template("index.html", data=latest_data)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    if not data or 'device_id' not in data:
        return "Invalid data", 400
    latest_data[data['device_id']] = data
    print("Received:", data)
    return "Data received", 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(latest_data)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
