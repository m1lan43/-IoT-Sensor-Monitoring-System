import socket
import sys
from messages import encode_message

HOST = "127.0.0.1"
PORT = 5000

def main():
    sensor_id = sys.argv[1]

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    message = encode_message({
        "type": "SENSOR_LOGIN",
        "sensor_id": sensor_id
    })

    client.sendall(message)

    reader = client.makefile("r")
    reply = reader.readline()
    print(reply)

    reader.close()
    client.close()


if __name__ == "__main__":
    main()
