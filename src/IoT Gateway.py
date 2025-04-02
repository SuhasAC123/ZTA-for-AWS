import time
import serial
import paho.mqtt.client as mqtt
import ssl
import json  # Required for JSON serialization

# Serial port configuration
arduino_port = "COM3"  # Replace with your Arduino's port
baud_rate = 9600
try:
    arduino = serial.Serial(arduino_port, baud_rate)
    print("Successfully connected to Arduino.")
except Exception as e:
    print(f"Failed to connect to Arduino: {e}")
    exit()

# AWS IoT Core configuration
aws_endpoint = "a2k3pzzo7jmz3z-ats.iot.ap-south-1.amazonaws.com"
port = 8883
ca_path = r"C:\\Users\\suhas\\OneDrive\\Desktop\\Zero Trust\\AmazonRootCA1.pem"
cert_path = r"C:\\Users\\suhas\\OneDrive\\Desktop\\Zero Trust\\a384c01b39def3ea3934d35f67b2c21cf9d5f9381dd46670bdaa24d4df005a21-certificate.pem.crt"
key_path = r"C:\\Users\\suhas\\OneDrive\\Desktop\\Zero Trust\\a384c01b39def3ea3934d35f67b2c21cf9d5f9381dd46670bdaa24d4df005a21-private.pem.key"
mqtt_topic = "SensorData"  # MQTT topic to publish sensor data

# MQTT client setup
client = mqtt.Client()
try:
    client.tls_set(
        ca_certs=ca_path,
        certfile=cert_path,
        keyfile=key_path,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLSv1_2,
    )
    print("TLS configuration set successfully.")
except Exception as e:
    print(f"Failed to configure TLS: {e}")
    exit()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to AWS IoT Core")
    else:
        print(f"Failed to connect, return code {rc}")

client.on_connect = on_connect
try:
    client.connect(aws_endpoint, port, keepalive=60)
except Exception as e:
    print(f"Failed to connect to AWS IoT Core: {e}")
    exit()

# Main loop to read data from Arduino and send it to AWS IoT Core
try:
    client.loop_start()
    while True:
        if arduino.in_waiting > 0:
            # Read data from Arduino
            raw_data = arduino.readline().decode("utf-8").strip()
            try:
                # Parse the data (expected format: "SensorType,Value,Units")
                sensor_type, reading, units = raw_data.split(",")

                # Generate timestamp
                timestamp = int(time.time())

                # Create JSON payload
                payload = {
                    "SensorID": sensor_type,
                    "TS": timestamp,
                    "Reading": float(reading),  # Convert reading to float for numerical data
                    "Units": units,
                }

                # Convert the payload to a JSON string
                payload_json = json.dumps(payload)

                # Publish data to AWS IoT Core
                client.publish(mqtt_topic, payload_json)
                print(f"Published: {payload_json}")
            except ValueError:
                print(f"Invalid data format: {raw_data}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.loop_stop()
    arduino.close()
    print("Closed connections.")
