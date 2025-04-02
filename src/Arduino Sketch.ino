#include <DHT.h>

// Pin Definitions
#define DHTPIN 2       // Pin where the DHT11 data pin is connected
#define DHTTYPE DHT11  // Define the type of DHT sensor (DHT11)
const int trigPin = 9;  // Ultrasonic sensor Trigger pin
const int echoPin = 10; // Ultrasonic sensor Echo pin

// Initialize the DHT sensor
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Start the DHT sensor
  dht.begin();

  // Initialize ultrasonic sensor pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

}

void loop() {
  // Reading data from the DHT11 sensor
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Reading data from the ultrasonic sensor
  long duration;
  float distance;

  // Clear the trigger pin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Trigger the sensor by sending a HIGH pulse of 10 microseconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read the echo pin, and calculate the distance
  duration = pulseIn(echoPin, HIGH);
  distance = (duration * 0.034) / 2; // Speed of sound in cm/us, divided by 2 for round trip

  // Check if any DHT reading failed
if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor");
} else {
    // Output in the desired format
    Serial.print("distance,");
    Serial.print(distance);
    Serial.println(",cm");

    Serial.print("temperature,");
    Serial.print(temperature);
    Serial.println(",°C");

    Serial.print("humidity,");
    Serial.print(humidity);
    Serial.println(",%");
}


  // Delay to avoid overwhelming the serial monitor
  delay(2000);
}
