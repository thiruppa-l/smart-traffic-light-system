# Smart Traffic Light System 🚦

A smart traffic control system that uses YOLOv5 object detection and ESP8266 to prioritize green signals based on vehicle density.

## 🔧 Tech Stack
- YOLOv5 (Python)
- ESP8266 (Arduino C++)
- Flutter (Mobile UI)

## 📂 Project Structure
- `python_code/`: Object detection using YOLOv5
- `esp_code/`: Node priority controller for traffic signals
- `flutter_app/`: UI to display signal status

## ⚙️ How it Works
1. Camera feed is analyzed using YOLOv5
2. Vehicles are counted and density is calculated
3. ESP8266 assigns signal based on the density
4. Flutter app shows which node has green, yellow, or red

## ⚠️ Note
This project is for educational/demo purposes.
