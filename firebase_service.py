import datetime
import firebase_admin
from firebase_admin import credentials, db
import os

class FirebaseManager:
    def __init__(self, cred_path='serviceAccountKey.json', db_url=None):
        self.mock_mode = False
        self.memory_alerts = []

        if os.path.exists(cred_path) and db_url and 'your-firebase' not in db_url:
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {'databaseURL': db_url})
                self.ref = db.reference('aegis_alerts')
            except Exception as e:
                print(f"[AegisGuard] Firebase init failed: {e}. Falling back to in-memory mode.")
                self.mock_mode = True
        else:
            print("[AegisGuard] Notice: Firebase credentials not found or unconfigured. Running in Mock/In-Memory Mode.")
            self.mock_mode = True

    def push_alert(self, alert_type, confidence, lat=None, lon=None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "type": alert_type,
            "confidence": f"{confidence:.2f}%",
            "timestamp": timestamp,
            "latitude": lat if lat else "18.5204",
            "longitude": lon if lon else "73.8567",
            "status": "Active / Unacknowledged"
        }

        if not self.mock_mode:
            new_ref = self.ref.push()
            new_ref.set(record)
            record["id"] = new_ref.key
        else:
            record["id"] = f"mock_{len(self.memory_alerts) + 1}"
            self.memory_alerts.insert(0, record)

        return record

    def get_recent_alerts(self, limit=10):
        if not self.mock_mode:
            data = self.ref.order_by_key().limit_to_last(limit).get()
            if not data:
                return []
            alerts = []
            for k, v in data.items():
                v['id'] = k
                alerts.append(v)
            alerts.reverse()
            return alerts
        return self.memory_alerts[:limit]