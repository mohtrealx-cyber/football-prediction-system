import json
import unittest
from dataclasses import dataclass
from datetime import datetime, timezone

from pipeline.daily_report_serializer import serialize_daily_report


@dataclass
class FakeSelection:
    match_id: str
    selection: str
    odds: float


@dataclass
class FakeTicket:
    name: str
    stake_percent: float
    selections: list


class DailyReportSerializerTests(unittest.TestCase):

    def setUp(self):
        self.as_of = datetime(
            2026,
            9,
            25,
            12,
            0,
            tzinfo=timezone.utc,
        )

    def test_no_bet_report_is_serialized(self):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        result = serialize_daily_report(report)

        self.assertIsInstance(result, dict)
        self.assertEqual(
            result["report_type"],
            "DAILY_FOOTBALL_REPORT",
        )
        self.assertEqual(
            result["status"],
            "NO_BET",
        )

    def test_datetime_is_converted_to_iso_string(self):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        result = serialize_daily_report(report)

        self.assertIsInstance(
            result["as_of"],
            str,
        )
        self.assertEqual(
            result["as_of"],
            "2026-09-25T12:00:00+00:00",
        )

    def test_dataclass_objects_are_converted_to_dictionaries(self):
        selection = FakeSelection(
            match_id="m1",
            selection="HOME",
            odds=1.80,
        )

        ticket = FakeTicket(
            name="SAFE",
            stake_percent=40.0,
            selections=[selection],
        )

        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "READY",
            "as_of": self.as_of,
            "fixtures_received": 1,
            "upcoming_fixtures": 1,
            "portfolio": [
                ticket,
            ],
        }

        result = serialize_daily_report(report)

        self.assertIsInstance(
            result["portfolio"],
            list,
        )

        self.assertIsInstance(
            result["portfolio"][0],
            dict,
        )

        self.assertEqual(
            result["portfolio"][0]["name"],
            "SAFE",
        )

        self.assertEqual(
            result["portfolio"][0]["stake_percent"],
            40.0,
        )

        self.assertIsInstance(
            result["portfolio"][0]["selections"][0],
            dict,
        )

        self.assertEqual(
            result["portfolio"][0]["selections"][0]["match_id"],
            "m1",
        )

    def test_serialized_report_can_be_json_encoded_without_default_handler(
        self,
    ):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        result = serialize_daily_report(report)

        serialized = json.dumps(result)

        self.assertIsInstance(
            serialized,
            str,
        )

    def test_serialized_report_round_trip_preserves_core_fields(self):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 10,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        result = serialize_daily_report(report)

        restored = json.loads(
            json.dumps(result)
        )

        self.assertEqual(
            restored["report_type"],
            "DAILY_FOOTBALL_REPORT",
        )

        self.assertEqual(
            restored["status"],
            "NO_BET",
        )

        self.assertEqual(
            restored["fixtures_received"],
            10,
        )

        self.assertEqual(
            restored["upcoming_fixtures"],
            0,
        )

    def test_original_report_is_not_modified(self):
        report = {
            "report_type": "DAILY_FOOTBALL_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        original_as_of = report["as_of"]

        result = serialize_daily_report(report)

        self.assertIsNot(
            result,
            report,
        )

        self.assertEqual(
            report["as_of"],
            original_as_of,
        )

        self.assertIsInstance(
            report["as_of"],
            datetime,
        )

    def test_non_dictionary_report_is_rejected(self):
        with self.assertRaises(TypeError):
            serialize_daily_report([])

    def test_missing_report_type_is_rejected(self):
        report = {
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        with self.assertRaises(ValueError):
            serialize_daily_report(report)

    def test_invalid_report_type_is_rejected(self):
        report = {
            "report_type": "WRONG_REPORT",
            "status": "NO_BET",
            "as_of": self.as_of,
            "fixtures_received": 0,
            "upcoming_fixtures": 0,
            "portfolio": {
                "status": "NO_BET",
                "reason": "insufficient qualifying selections",
                "tickets": [],
            },
        }

        with self.assertRaises(ValueError):
            serialize_daily_report(report)


if __name__ == "__main__":
    unittest.main()
