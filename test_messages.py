import json
import unittest

from messages import (
    ProtocolError,
    SensorStore,
    encode_message,
    make_error,
    make_ok,
    make_readings,
    parse_message,
)


class TestParse(unittest.TestCase):
    def test_sensor_login(self):
        msg = parse_message('{"type":"SENSOR_LOGIN","sensor_id":"S1"}')
        self.assertEqual(msg["sensor_id"], "S1")

    def test_sensor_data_from_bytes(self):
        raw = b'{"type":"SENSOR_DATA","sensor_id":"S1","temperature":25.5,"humidity":40}\n'
        msg = parse_message(raw)
        self.assertEqual(msg["temperature"], 25.5)

    def test_get_readings(self):
        self.assertEqual(parse_message('{"type":"GET_READINGS"}')["type"], "GET_READINGS")

    def test_bad_json(self):
        with self.assertRaises(ProtocolError):
            parse_message("not json")

    def test_empty(self):
        with self.assertRaises(ProtocolError):
            parse_message("   \n")

    def test_not_an_object(self):
        with self.assertRaises(ProtocolError):
            parse_message("[1, 2, 3]")

    def test_missing_type(self):
        with self.assertRaises(ProtocolError):
            parse_message('{"sensor_id":"S1"}')

    def test_unknown_type(self):
        with self.assertRaises(ProtocolError):
            parse_message('{"type":"HELLO"}')

    def test_missing_field(self):
        with self.assertRaises(ProtocolError):
            parse_message('{"type":"SENSOR_DATA","sensor_id":"S1","temperature":20}')

    def test_wrong_field_type(self):
        with self.assertRaises(ProtocolError):
            parse_message('{"type":"SENSOR_DATA","sensor_id":"S1","temperature":"hot","humidity":40}')

    def test_bool_rejected_as_number(self):
        with self.assertRaises(ProtocolError):
            parse_message('{"type":"SENSOR_DATA","sensor_id":"S1","temperature":true,"humidity":40}')

    def test_empty_sensor_id(self):
        with self.assertRaises(ProtocolError):
            parse_message('{"type":"SENSOR_LOGIN","sensor_id":"  "}')

    def test_bad_bytes(self):
        with self.assertRaises(ProtocolError):
            parse_message(b"\xff\xfe\xfa")


class TestEncode(unittest.TestCase):
    def test_ends_with_newline(self):
        self.assertTrue(encode_message(make_ok()).endswith(b"\n"))

    def test_round_trip(self):
        data = {"S1": {"temperature": 25.5, "humidity": 40}}
        decoded = json.loads(encode_message(make_readings(data)))
        self.assertEqual(decoded["type"], "READINGS")
        self.assertEqual(decoded["data"], data)

    def test_error_message(self):
        self.assertEqual(make_error("bad")["type"], "ERROR")


class TestStore(unittest.TestCase):
    def test_latest_reading_wins(self):
        store = SensorStore()
        store.update("S1", 20, 30)
        store.update("S1", 25.5, 40)
        store.update("S2", 18, 55)
        snap = store.snapshot()
        self.assertEqual(snap["S1"], {"temperature": 25.5, "humidity": 40})
        self.assertEqual(len(snap), 2)

    def test_snapshot_is_a_copy(self):
        store = SensorStore()
        store.update("S1", 20, 30)
        store.snapshot()["S1"]["temperature"] = 999
        self.assertEqual(store.snapshot()["S1"]["temperature"], 20)


if __name__ == "__main__":
    unittest.main()
