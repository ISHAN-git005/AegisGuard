from flask import Flask, render_template, Response, request, jsonify
from config import Config
from detector import SafetyDetector
from firebase_service import FirebaseManager

app = Flask(__name__)
app.config.from_object(Config)

fb_manager = FirebaseManager(
    cred_path=app.config['FIREBASE_CREDENTIALS'],
    db_url=app.config['FIREBASE_DATABASE_URL']
)

def on_vision_incident(incident_type, confidence):
    fb_manager.push_alert(incident_type, confidence)

detector = SafetyDetector(alert_callback=on_vision_incident)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    alerts = fb_manager.get_recent_alerts(15)
    return render_template('dashboard.html', alerts=alerts)

@app.route('/video_feed')
def video_feed():
    return Response(detector.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/sos', methods=['POST'])
def trigger_sos():
    data = request.get_json() or {}
    lat = data.get('lat')
    lon = data.get('lon')
    record = fb_manager.push_alert("Manual SOS Panic Button", 100.0, lat, lon)
    return jsonify({"status": "success", "alert": record}), 200

@app.route('/api/alerts', methods=['GET'])
def fetch_alerts():
    alerts = fb_manager.get_recent_alerts(20)
    return jsonify(alerts), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)