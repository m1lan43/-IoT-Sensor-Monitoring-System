import socket
import sys
import time
import random
import json

from messages import encode_message

HOST = "127.0.0.1"
PORT = 6000

sensor_id = sys.argv[1] if len(sys.argv) > 1 else "S1"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
    print("Connected to server")

    with client.makefile("rb") as reader:

        login = {
            "type": "SENSOR_LOGIN",
            "sensor_id": sensor_id
        }

        client.sendall(encode_message(login))

        response = json.loads(reader.readline().decode("utf-8"))
        print("Login response:", response)

        if response["type"] != "OK":
            raise RuntimeError("Sensor login failed")

        for i in range(5):
            temperature = round(random.uniform(20, 35), 2)
            humidity = round(random.uniform(30, 70), 2)

            data = {
                "type": "SENSOR_DATA",
                "sensor_id": sensor_id,
                "temperature": temperature,
                "humidity": humidity
            }

            client.sendall(encode_message(data))

            response = json.loads(reader.readline().decode("utf-8"))

            print("Reading sent:", data)
            print("Server response:", response)

            time.sleep(2)

        client.sendall(encode_message({
            "type": "DISCONNECT"
        }))

        response = json.loads(reader.readline().decode("utf-8"))
        print("Disconnect response:", response)

except (OSError, RuntimeError, ValueError) as e:
    print("Error:", e)

finally:
    client.close()
    print("Connection closed")
