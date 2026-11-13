"""Message format helpers for the IoT Sensor Collector.

Wire format: one JSON object per line, ending in "\n".
This module has no socket code, so it can be tested on its own.
"""
import json
import threading

# Client -> server message types and the fields each one must contain.
# Each field maps to the Python type(s) it must have.
NUMBER = (int, float)
REQUIRED_FIELDS = {
    "SENSOR_LOGIN": {"sensor_id": str},
    "SENSOR_DATA": {"sensor_id": str, "temperature": NUMBER, "humidity": NUMBER},
    "VIEWER_LOGIN": {},
    "GET_READINGS": {},
    "DISCONNECT": {},
}


class ProtocolError(Exception):
    """Raised when an incoming message is invalid."""


def parse_message(raw):
    """Turn a raw line (str or bytes) into a validated dict.

    Raises ProtocolError with a readable reason if anything is wrong,
    so the server can reply with an ERROR message instead of crashing.
    """
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise ProtocolError("message is not valid UTF-8")

    raw = raw.strip()
    if not raw:
        raise ProtocolError("empty message")

    try:
        msg = json.loads(raw)
    except json.JSONDecodeError:
        raise ProtocolError("message is not valid JSON")

    if not isinstance(msg, dict):
        raise ProtocolError("message must be a JSON object")

    msg_type = msg.get("type")
    if msg_type is None:
        raise ProtocolError("missing 'type' field")
    if msg_type not in REQUIRED_FIELDS:
        raise ProtocolError(f"unknown message type: {msg_type}")

    for field, expected in REQUIRED_FIELDS[msg_type].items():
        if field not in msg:
            raise ProtocolError(f"{msg_type} is missing '{field}'")
        value = msg[field]
        # bool is a subclass of int in Python, so reject it explicitly.
        if isinstance(value, bool) or not isinstance(value, expected):
            raise ProtocolError(f"'{field}' has the wrong type in {msg_type}")

    if "sensor_id" in REQUIRED_FIELDS[msg_type] and not msg["sensor_id"].strip():
        raise ProtocolError("'sensor_id' must not be empty")

    return msg


def encode_message(msg):
    """Turn a dict into bytes ready for sock.sendall()."""
    return (json.dumps(msg) + "\n").encode("utf-8")


# Builders for the messages the server sends back.
def make_ok(text="OK"):
    return {"type": "OK", "message": text}


def make_error(reason):
    return {"type": "ERROR", "message": reason}


def make_readings(data):
    return {"type": "READINGS", "data": data}


class SensorStore:
    """Holds the latest reading from each sensor. Safe to share between threads."""

    def __init__(self):
        self._readings = {}
        self._lock = threading.Lock()

    def update(self, sensor_id, temperature, humidity):
        with self._lock:
            self._readings[sensor_id] = {
                "temperature": temperature,
                "humidity": humidity,
            }

    def snapshot(self):
        """Return a copy of all latest readings."""
        with self._lock:
            return {sid: dict(r) for sid, r in self._readings.items()}
