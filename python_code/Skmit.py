import tkinter as tk
import threading
import time
import cv2
import torch
from PIL import Image, ImageTk
import requests

class SmartTrafficLightApp:
    def _init_(self, root, video_sources):

        self.root = root
        self.root.title("COMPUTER VISION BASED ENHANCED TRAFFIC MANAGEMENT SYSTEM")
        self.root.geometry("1000x400")
        self.root.configure(bg="#f0f0f0")

        # Load YOLOv5 model
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)

        # Initialize densities, timers, traffic lights, cycle count, and speed
        self.densities = [0] * 4
        self.timers = [0] * 4
        self.traffic_lights = ['Red'] * 4
        self.junctions = list(range(4))
        self.simulation_running = False
        self.cycle_count = 0
        self.video_sources = video_sources
        self.caps = [None] * 4  # For storing VideoCapture objects
        self.current_frames = [0] * 4  # Store current frame positions

        # Set up the GUI layout
        self.setup_gui()

    def setup_gui(self):
        title_frame = tk.Frame(self.root, bg="#f0f0f0")
        title_frame.pack(pady=10)
        title_label = tk.Label(title_frame, text="Smart Traffic Light Simulation", font=("Helvetica", 24, "bold"), bg="#f0f0f0")
        title_label.pack()

        videos_frame = tk.Frame(self.root, bg="#f0f0f0")
        videos_frame.pack()

        self.image_labels = []
        self.density_labels = []
        self.light_labels = []
        self.countdown_labels = []

        for i in range(4):
            frame = tk.Frame(videos_frame, borderwidth=2, relief='groove', bg="#f0f0f0")
            frame.grid(row=0, column=i, padx=10, pady=10)

            image_label = tk.Label(frame)
            image_label.pack()
            self.image_labels.append(image_label)

            density_label = tk.Label(frame, text=f"Density: {self.densities[i]}", font=("Helvetica", 14), bg="#f0f0f0")
            density_label.pack()
            self.density_labels.append(density_label)

            light_label = tk.Label(frame, text=f"Traffic Light: {self.traffic_lights[i]}", font=("Helvetica", 16), bg="#f0f0f0")
            light_label.pack()
            self.light_labels.append(light_label)

            countdown_value = tk.Label(frame, text="0", font=("Helvetica", 14), bg="#f0f0f0")
            countdown_value.pack()
            self.countdown_labels.append(countdown_value)

        self.cycle_count_label = tk.Label(self.root, text="Cycle Count: 0", font=("Helvetica", 16), bg="#f0f0f0")
        self.cycle_count_label.pack(pady=10)

        start_button = tk.Button(self.root, text="Start Simulation", command=self.start_simulation, bg="#4CAF50", fg="white", font=("Helvetica", 16))
        start_button.pack(pady=20)

        self.speed_slider = tk.Scale(self.root, from_=1, to=4, orient=tk.HORIZONTAL, label="Simulation Speed (1x to 4x)", bg="#f0f0f0")
        self.speed_slider.set(1)
        self.speed_slider.pack(pady=10)

    def process_video(self, video_source, idx):
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"Error: Unable to open video source {video_source}")
            return

        self.caps[idx] = cap  # Store the VideoCapture object

        while self.simulation_running:
            if self.traffic_lights[idx] == 'Green':
                ret, frame = cap.read()
                if ret:
                    self.current_frames[idx] += 1
                    frame = cv2.resize(frame, (320, 240))  # Resize for consistency
                    self.detect_vehicles(frame, idx)

                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_tk = ImageTk.PhotoImage(img_pil)

                    # Update the video display label
                    self.image_labels[idx].config(image=img_tk)
                    self.image_labels[idx].image = img_tk  # Keep a reference
                else:
                    break
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frames[idx])  # Pause the video

            self.root.update_idletasks()
            time.sleep(0.03)  # Control playback speed

        cap.release()

    def detect_vehicles(self, frame, idx):
        results = self.model(frame)
        detections = results.xyxy[0]

        # Filter vehicle classes (car, motorcycle, bus, truck)
        vehicle_classes = [2, 3, 5, 7]  # COCO classes for vehicles
        vehicle_detections = [d for d in detections if int(d[5]) in vehicle_classes]

        # Update density
        self.densities[idx] = len(vehicle_detections)

        # Draw bounding boxes on the frame
        for *box, conf, cls in vehicle_detections:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw bounding box

    def start_simulation(self):
        if not self.simulation_running:
            self.simulation_running = True
            for i, video_source in enumerate(self.video_sources):
                threading.Thread(target=self.process_video, args=(video_source, i), daemon=True).start()
            threading.Thread(target=self.control_traffic_lights, daemon=True).start()

    def control_traffic_lights(self):
        while self.simulation_running:
            # Sort junctions based on density (highest first)
            sorted_junctions = sorted(self.junctions, key=lambda x: self.densities[x], reverse=True)

            for junction in sorted_junctions:
                # Set all traffic lights to red
                for i in range(4):
                    self.traffic_lights[i] = 'Red'
                    self.timers[i] = 0
                    self.countdown_labels[i].config(text="0")
                    self.update_info(i)  # Update UI for red lights

                # Set green light for the current junction
                self.traffic_lights[junction] = 'Green'
                
                # Calculate duration based on density
                base_time = 5  # Base time in seconds
                additional_time_per_vehicle = 1  # Additional time for each vehicle detected
                self.timers[junction] = base_time + (self.densities[junction] * additional_time_per_vehicle)

                self.update_info(junction)

                # Send HTTP request to update traffic light
                state = "green"
                requests.get(f"http://192.168.137.27/setLight?junction={junction}&state={state}")

                # Timer countdown
                for remaining_time in range(self.timers[junction], 0, -1):
                    self.update_gui(remaining_time, junction)
                    time.sleep(1 / self.speed_slider.get())  # Adjust sleep based on slider value

                self.cycle_count += 1
                self.cycle_count_label.config(text=f"Cycle Count: {self.cycle_count}")
                time.sleep(0.5 / self.speed_slider.get())  # Short pause between cycles

    def update_info(self, active_junction):
        for i in range(4):
            self.density_labels[i].config(text=f"Density: {self.densities[i]}")
            self.light_labels[i].config(text=f"Traffic Light: {self.traffic_lights[i]}")

            if self.traffic_lights[i] == 'Green':
                self.light_labels[i].config(bg="green", fg="white")
            else:
                self.light_labels[i].config(bg="red", fg="white")

    def update_gui(self, countdown, active_junction):
        for i in range(4):
            self.density_labels[i].config(text=f"Density: {self.densities[i]}")
            self.light_labels[i].config(text=f"Traffic Light: {self.traffic_lights[i]}")
            if i == active_junction:
                self.countdown_labels[i].config(text=str(countdown))

        self.root.update_idletasks()

if _name_ == "_main_":

    root = tk.Tk()
    video_sources = ['1.mp4', '2.mp4', '3.mp4', '4.mp4']  # Replace with your video file paths
    app = SmartTrafficLightApp(root, video_sources)
    root.mainloop()