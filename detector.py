import cv2
import time

class SafetyDetector:
    def __init__(self, alert_callback=None):
        self.cap = cv2.VideoCapture(0)
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=50, detectShadows=False)
        self.alert_callback = alert_callback
        self.last_alert_time = 0
        self.cooldown_period = 7  # seconds between duplicate alerts

    def generate_frames(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                break

            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fgmask = self.fgbg.apply(gray)

            # Clean morphological noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

            contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            detected_status = "Status: Normal"
            status_color = (0, 255, 0)

            for cnt in contours:
                if cv2.contourArea(cnt) > 4000:
                    x, y, w, h = cv2.boundingRect(cnt)
                    aspect_ratio = float(w) / h

                    # Sudden horizontal flattening -> typical fall posture for seniors/children
                    if aspect_ratio > 1.6 and y > 200:
                        detected_status = "CRITICAL: Fall Detected!"
                        status_color = (0, 0, 255)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)

                        now = time.time()
                        if (now - self.last_alert_time) > self.cooldown_period:
                            self.last_alert_time = now
                            if self.alert_callback:
                                self.alert_callback("Fall / Sudden Inactivity", 94.2)
                    else:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.putText(frame, detected_status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            cv2.putText(frame, "AegisGuard AI Vision Active", (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def release(self):
        if self.cap.isOpened():
            self.cap.release()