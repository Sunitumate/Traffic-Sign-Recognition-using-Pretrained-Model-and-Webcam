import cv2
import numpy as np
import pyttsx3
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import queue

class SmartTrafficApp:
    def __init__(self, window):
        self.window = window
        self.window.title("🚦 Smart Traffic & Human Detection System")
        self.window.geometry("900x700")
        self.window.configure(bg="#e6f7ff")

        # Video display frame
        self.video_frame = tk.Label(window, bg="black")
        self.video_frame.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(window, bg="#e6f7ff")
        btn_frame.pack(pady=5)

        self.start_btn = tk.Button(btn_frame, text="▶ Start Detection", command=self.start_detection, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.start_btn.grid(row=0, column=0, padx=10)

        self.stop_btn = tk.Button(btn_frame, text="⛔ Stop Detection", command=self.stop_detection, state=tk.DISABLED, bg="#f44336", fg="white", font=("Arial", 12))
        self.stop_btn.grid(row=0, column=1, padx=10)

        # Status
        self.status = tk.Label(window, text="Status: Stopped", bg="#e6f7ff", fg="red", font=("Arial", 14, "bold"))
        self.status.pack(pady=5)

        # Detection history
        self.history_label = tk.Label(window, text="Detection History", bg="#e6f7ff", font=("Arial", 12, "underline"))
        self.history_label.pack()

        self.history_box = tk.Listbox(window, height=10, width=70)
        self.history_box.pack(pady=5)

        # Counter
        self.count_label = tk.Label(window, text="Total Detections: 0", bg="#e6f7ff", fg="black", font=("Arial", 12, "bold"))
        self.count_label.pack(pady=5)

        # Detection Engine
        self.cap = None
        self.running = False
        self.detection_count = 0
        self.last_alert = ""
        self.history = []
        self.queue = queue.Queue()

        threading.Thread(target=self.speak_alerts, daemon=True).start()

        # Haar cascades
        self.full_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        self.upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def speak_alerts(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)   # Speed of speech
        engine.setProperty('volume', 1.0) # Max volume
        while True:
            text = self.queue.get()
            engine.say(text)
            engine.runAndWait()
            self.queue.task_done()

    def detect_objects(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        masks = {
            'Red': cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255])) +
                   cv2.inRange(hsv, np.array([170, 70, 50]), np.array([180, 255, 255])),
            'Yellow': cv2.inRange(hsv, np.array([20, 100, 100]), np.array([30, 255, 255])),
            'Green': cv2.inRange(hsv, np.array([40, 50, 50]), np.array([90, 255, 255]))
        }

        detections = []
        for color, mask in masks.items():
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) > 1000:
                    x, y, w, h = cv2.boundingRect(cnt)
                    detections.append((color, x, y, w, h))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        humans = list(self.full_body_cascade.detectMultiScale(gray, 1.1, 4)) + \
                 list(self.upper_body_cascade.detectMultiScale(gray, 1.1, 4)) + \
                 list(self.face_cascade.detectMultiScale(gray, 1.1, 4))

        return detections, humans

    def start_detection(self):
        if not self.running:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status.config(text="Status: Running", fg="green")
            threading.Thread(target=self.video_loop, daemon=True).start()

    def stop_detection(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status.config(text="Status: Stopped", fg="red")
        if self.cap:
            self.cap.release()
        self.video_frame.config(image='')

    def video_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            signs, humans = self.detect_objects(frame)

            for (color, x, y, w, h) in signs:
                label = f"{color} Sign"
                color_code = {'Red': (0, 0, 255), 'Yellow': (0, 255, 255), 'Green': (0, 255, 0)}[color]
                cv2.rectangle(frame, (x, y), (x + w, y + h), color_code, 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_code, 2)
                self.handle_alert(f"{label} detected")

            for (x, y, w, h) in humans:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, 'Human Detected', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                self.handle_alert("Human Detected - Please slow down")

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)

        self.stop_detection()

    def handle_alert(self, message):
        if message != self.last_alert:
            self.queue.put(message)
            self.last_alert = message
            self.detection_count += 1
            timestamp = time.strftime('%H:%M:%S')
            log = f"{timestamp} - {message}"
            self.history.append(log)
            self.history_box.insert(tk.END, log)
            if self.history_box.size() > 10:
                self.history_box.delete(0)
            self.count_label.config(text=f"Total Detections: {self.detection_count}")

if __name__ == '__main__':
    root = tk.Tk()
    app = SmartTrafficApp(root)
    root.mainloop()
