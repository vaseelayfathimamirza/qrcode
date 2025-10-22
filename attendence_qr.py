import qrcode
import cv2
import pandas as pd
import datetime
import os
import time

# ---------- STEP 1: GENERATE QR CODES ----------
students = {
    "2021CS101": "Rahul Sharma",
    "2021CS102": "Anita Verma",
    "2021CS103": "Ravi Kumar",
    "2021CS104": "Fathima"
}

# Create folder if not exists
os.makedirs("qrcodes", exist_ok=True)

for sid, name in students.items():
    qr = qrcode.make(sid)
    qr.save(f"qrcodes/{sid}.png")

print("✅ QR Codes Generated Successfully!\n")

# ---------- STEP 2: SETUP ATTENDANCE CSV ----------
filename = "attendance.csv"
if not os.path.exists(filename):
    df = pd.DataFrame(columns=["StudentID", "Name", "Date", "Time"])
    df.to_csv(filename, index=False)

# ---------- STEP 3: OPEN CAMERA AND SCAN ----------
print("📷 Show your QR Code to the camera... Press ESC to stop.\n")
cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

# Track attendance and cooldown
today = str(datetime.date.today())
df = pd.read_csv(filename)
marked_today = set(df.loc[df["Date"] == today, "StudentID"])
cooldown = {}  # Track last detection time per student
COOLDOWN_TIME = 3  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera not accessible")
        break

    data, bbox, _ = detector.detectAndDecode(frame)
    if data:
        student_id = data.strip()
        now_time = time.time()

        # Process only if cooldown passed
        if student_id not in cooldown or (now_time - cooldown[student_id]) > COOLDOWN_TIME:
            cooldown[student_id] = now_time
            print(f"Detected: {student_id}")

            if student_id in students:
                name = students[student_id]
                now = datetime.datetime.now()

                if student_id not in marked_today:
                    new_entry = {
                        "StudentID": student_id,
                        "Name": name,
                        "Date": today,
                        "Time": now.strftime("%H:%M:%S")
                    }
                    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                    df.to_csv(filename, index=False)
                    marked_today.add(student_id)

                    print(f"✅ Attendance marked for {name} ({student_id}) at {now.strftime('%H:%M:%S')}")
                    cv2.putText(frame, f"{name} Marked Present", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                else:
                    # Already marked
                    print(f"⚠️ {name} ({student_id}) already marked today.")
                    cv2.putText(frame, f"{name} Already Marked", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
            else:
                print(f"❌ Unknown QR detected: {student_id}")
                cv2.putText(frame, "Unknown QR Code", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow("QR Attendance System", frame)
    if cv2.waitKey(1) == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
