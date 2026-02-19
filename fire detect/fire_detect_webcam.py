import cv2
import pyttsx3
import geocoder
from twilio.rest import Client
from ultralytics import YOLO

# === Configuration ===
model_path = r"C:\Users\velev\runs\detect\fire_model_v12\weights\best.pt"
twilio_sid = "ACac3fe7f95457f6f95d6a9f1a29127db0"
twilio_auth = "56b8d6e045cc03cd53584ab47b44ee2a"
twilio_number = "+12513468728"       # Twilio phone number
to_number = "+918317502668"       # Emergency contact

# === Initialize YOLOv8 Model ===
model = YOLO(model_path)

# === Initialize Text-to-Speech ===
engine = pyttsx3.init()

# === Twilio Setup ===
client = Client(twilio_sid, twilio_auth)

# === Capture from webcam ===
cap = cv2.VideoCapture(0)

fire_alerted = False

def speak_alert():
    engine.say("🔥 Fire detected in the building. Please evacuate immediately!")
    engine.runAndWait()

def send_twilio_call():
    try:
        call = client.calls.create(
            url='http://demo.twilio.com/docs/voice.xml',
            to=to_number,
            from_=twilio_number
        )
        print(f"[📞] Call initiated: SID {call.sid}")
    except Exception as e:
        print(f"[❌] Error making call: {e}")

def send_location_sms():
    try:
        g = geocoder.ip('me')
        location = g.latlng
        message = f"🚨 Fire Alert!\nLocation: https://www.google.com/maps?q={location[0]},{location[1]}"
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=to_number
        )
        print(f"[📍] Location sent: {message}")
    except Exception as e:
        print(f"[❌] Location error: {e}")

# === Main Loop ===
while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(source=frame, conf=0.5, verbose=False)

    fire_detected = False

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label_name = model.names[cls_id]

            if label_name == 'fire':
                fire_detected = True

                # Draw bounding box for fire
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                label = f"{label_name} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    if fire_detected and not fire_alerted:
        print("[🔥] Fire detected! Triggering alerts...")
        speak_alert()
        send_twilio_call()
        send_location_sms()
        fire_alerted = True

    cv2.imshow("🔥 Fire Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === Cleanup ===
cap.release()
cv2.destroyAllWindows()
