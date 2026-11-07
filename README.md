# IoT-Sensor-Monitoring-System
This project is a Simple IoT Sensor Collector where multiple simulated sensor clients send environmental readings to a central server. The server acts as a hub, storing the latest readings received from each sensor, while a separate viewer client can connect to request and display the current data in real-time.

# Problem Description and Intended Users

Managing data from distributed sensors often requires a centralized system to prevent data fragmentation. This system solves that by:
* Collecting readings from multiple simulated sensors in one central place.
* Storing and update the latest reading received from each sensor.
* Allowing viewer clients to request and view the current sensor readings.
* Supporting multiple clients communicating with the server at the same time.

Intended Users:
* This system is designed for users who need to monitor environmental information—such as temperature, humidity, and other metrics—and view the latest aggregated data from multiple remote sensors in a single interface.

# Main Features

* **Sensor Connection:** Multiple simulated sensors will be able to connect to the
server at the same time.
* **Sensor Identification:** Each sensor will identify itself when connecting so the
server can recognize where each reading is coming from.
* **Sending Sensor Readings:** The sensor clients will automatically send readings
to the server every few seconds.
* **Storing the Latest Readings:** The server will keep the most recent reading
received from each connected sensor.
* **Viewer Client:** A separate viewer client will be able to connect to the server and
request the latest sensor readings.
* **Displaying Current Readings:** When requested, the server will send the stored
readings to the viewer so they can be displayed clearly.
* **Client Disconnection:** Sensor and viewer clients will be able to disconnect
without interrupting the server or the other connected clients.
* **Basic Error Handling:** The server will handle incorrect messages or unexpected
disconnections without crashing.

# System Architecture & Protocol

The system utilizes a client-server architecture communicating over TCP sockets. All data exchanged between the server, sensors, and viewers is formatted as JSON messages. To handle multiple simultaneous connections, the server utilizes Python's threading capabilities.

# Tools and Libraries

**Python 3:** The core programming language used for the project.

**Built-in Python Modules:**

* **socket:** For establishing TCP communication between the server and clients.
* **threading:** To allow the server to manage multiple client connections concurrently.
* **json:** For encoding and decoding the message payloads.
* **time:** To manage the frequency of automated sensor data transmissions.

**Wireshark:** Used for network packet analysis to capture and inspect TCP traffic during testing and debugging.

**Git & GitHub:** For version control and team collaboration.
