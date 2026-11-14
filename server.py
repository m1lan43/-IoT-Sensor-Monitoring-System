
import socket
import threading

from messages import (
    parse_message,
    encode_message,
    make_ok,
    make_error,
    make_readings,
    ProtocolError,
    SensorStore
)

HOST = "127.0.0.1"
PORT = 6000

# Shared storage for all sensor readings
store = SensorStore()


def handle_client(client, address):
    print("Client connected:", address)

    role = None
    sensor_id = None

    try:
        with client:
            with client.makefile("rb") as reader:

                while True:
                    line = reader.readline()

                    # Client closed the connection
                    if not line:
                        break

                    try:
                        message = parse_message(line)
                        msg_type = message["type"]

                        print("Received:", message)

                        # Sensor login
                        if msg_type == "SENSOR_LOGIN":
                            if role is not None:
                                response = make_error("Already logged in")
                            else:
                                role = "sensor"
                                sensor_id = message["sensor_id"]
                                response = make_ok("Sensor logged in")

                        # Viewer login
                        elif msg_type == "VIEWER_LOGIN":
                            if role is not None:
                                response = make_error("Already logged in")
                            else:
                                role = "viewer"
                                response = make_ok("Viewer logged in")

                        # Receive sensor readings
                        elif msg_type == "SENSOR_DATA":
                            if role != "sensor":
                                response = make_error(
                                    "Sensor login required"
                                )

                            elif message["sensor_id"] != sensor_id:
                                response = make_error(
                                    "Sensor ID does not match login"
                                )

                            else:
                                store.update(
                                    sensor_id,
                                    message["temperature"],
                                    message["humidity"]
                                )

                                response = make_ok("Reading saved")

                        # Send readings to viewer
                        elif msg_type == "GET_READINGS":
                            if role != "viewer":
                                response = make_error(
                                    "Viewer login required"
                                )
                            else:
                                readings = store.snapshot()
                                response = make_readings(readings)

                        # Disconnect
                        elif msg_type == "DISCONNECT":
                            response = make_ok("Disconnected")
                            client.sendall(encode_message(response))
                            break

                        # Send response to client
                        client.sendall(encode_message(response))

                    except ProtocolError as e:
                        error = make_error(str(e))
                        client.sendall(encode_message(error))

    except (ConnectionError, OSError) as e:
        print("Connection error:", address, e)

    finally:
        print("Client disconnected:", address)


# Create TCP server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen()

print(f"Server is listening on {HOST}:{PORT}")

try:
    while True:
        client, address = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(client, address),
            daemon=True
        )

        thread.start()

except KeyboardInterrupt:
    print("\nServer stopped.")

finally:
    server.close()
