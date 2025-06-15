#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// Replace with your network credentials
const char* ssid = "monish";
const char* password = "11111111";

// Create a web server object
ESP8266WebServer server(80);

// Define pin numbers for each junction (Junction 1 and Junction 2)
const int junctions[2][3] = {
    {D1, D2, D3},  // Junction 1: Red on D1, Yellow on D2, Green on D3
    {D4, D5, D6}   // Junction 2: Red on D4, Yellow on D5, Green on D6
};

// Function to set the traffic light state
void setTrafficLight(int junction, const String& state) {
    // First, set all junctions to red
    for (int i = 0; i < 2; i++) {
        digitalWrite(junctions[i][0], HIGH);  // Red ON
        digitalWrite(junctions[i][1], LOW);   // Yellow OFF
        digitalWrite(junctions[i][2], LOW);   // Green OFF
    }

    // Now set the specified junction to the desired state
    if (junction < 0 || junction >= 2) return;
    Serial.println(state);


    if (state == "red") {
        digitalWrite(junctions[junction][0], HIGH);  // Red ON
        digitalWrite(junctions[junction][1], LOW);   // Yellow OFF
        digitalWrite(junctions[junction][2], LOW);   // Green OFF
    } else if (state == "green") {
        digitalWrite(junctions[junction][0], LOW);   // Red OFF
        digitalWrite(junctions[junction][1], LOW);   // Yellow OFF
        digitalWrite(junctions[junction][2], HIGH);  // Green ON
    } else if (state == "yellow") {
        digitalWrite(junctions[junction][0], LOW);   // Red OFF
        digitalWrite(junctions[junction][1], HIGH);  // Yellow ON
        digitalWrite(junctions[junction][2], LOW);   // Green OFF
    }
}

// Handle the HTTP request to set the traffic light
void handleSetLight() {
    int junction = server.arg("junction").toInt();
    String state = server.arg("state");

    setTrafficLight(junction, state);

    server.send(200, "text/plain", "Traffic light updated");
}

void setup() {
    Serial.begin(115200);

    // Initialize Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
    

    // Set pin modes for Junction 1 and 2
    for (int i = 0; i < 2; i++) {
        pinMode(junctions[i][0], OUTPUT); // Red
        pinMode(junctions[i][1], OUTPUT); // Yellow
        pinMode(junctions[i][2], OUTPUT); // Green
        setTrafficLight(i, "red"); // Set initial state to red
    }

    // Define the server route
    server.on("/setLight", handleSetLight);

    // Start the server
    server.begin();
    Serial.println("HTTP server started");
}

void loop() {
    server.handleClient();
}
