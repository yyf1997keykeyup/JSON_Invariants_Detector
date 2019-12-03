# coding=utf-8
import unittest
import json
import time

from src.util.const import HTTPMethodKey
from src.record_map.record_map import RecordMap
from src.converter.schema_generator import SchemaGenerator
from src.util.common import print_to_file


class TestPossibleType(unittest.TestCase):
    def setUp(self):
        self.schema_generator = SchemaGenerator()
        self.record_map = RecordMap()

    def test_not_exist_when_v1(self):
        """
        pattern 3
        """
        data_1 = {
            "log_id": 1,
            "log_type": "time_log",
            "log_timeline": []
        }
        data_2 = {
            "log_id": 9,
            "log_type": "event_log",
            "log_events": {}
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"log_id": 1},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)
        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"log_id": 9},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)

        self.record_map.load()

        """print to file"""
        # json_str = json.dumps(self.record_map.get_records(), indent=4)
        # print_to_file(json_str, file_name="../../output/pattern3/record.txt")

        invariant_schema = self.record_map.generate_invariant_schema()

        """print to file"""
        # json_str = json.dumps(invariant_schema, indent=4)
        # print_to_file(json_str, file_name="../../output/pattern3/invariant_schema.txt")

        log_timeline_pattern = invariant_schema["properties"]["log_timeline"]["not_exist_when"]
        log_events_pattern = invariant_schema["properties"]["log_events"]["not_exist_when"]

        assert log_timeline_pattern["request_params/log_id"] == [9]
        assert log_timeline_pattern["#/log_id"] == [9]
        assert log_timeline_pattern["#/log_type"] == ["event_log"]

        assert log_events_pattern["request_params/log_id"] == [1]
        assert log_events_pattern["#/log_id"] == [1]
        assert log_events_pattern["#/log_type"] == ["time_log"]

    def test_not_exist_when_v2(self):
        """
        pattern 3
        have duplicated data
        """
        data_1 = {
            "log_id": 1,
            "log_type": "time_log",
            "log_timeline": []
        }
        data_2 = {
            "log_id": 9,
            "log_type": "event_log",
            "log_events": {}
        }
        data_3 = {
            "log_id": 8,
            "log_type": "event_log",
            "log_events": {}
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"log_id": 1},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)
        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"log_id": 9},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)
        schema_3 = self.schema_generator.generate(json_dict=data_3,
                                                  request_params={"log_id": 8},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_3)
        self.record_map.load()

        """print to file"""
        # json_str = json.dumps(self.record_map.get_records(), indent=4)
        # print_to_file(json_str, file_name="../../output/pattern3/record.txt")

        invariant_schema = self.record_map.generate_invariant_schema()

        """print to file"""
        # json_str = json.dumps(invariant_schema, indent=4)
        # print_to_file(json_str, file_name="../../output/pattern3/invariant_schema.txt")

        log_timeline_pattern = invariant_schema["properties"]["log_timeline"]["not_exist_when"]
        log_events_pattern = invariant_schema["properties"]["log_events"]["not_exist_when"]

        assert len(log_timeline_pattern["request_params/log_id"]) == 2
        assert 8 in log_timeline_pattern["request_params/log_id"]
        assert 9 in log_timeline_pattern["request_params/log_id"]

        assert len(log_timeline_pattern["#/log_id"]) == 2
        assert 8 in log_timeline_pattern["#/log_id"]
        assert 9 in log_timeline_pattern["#/log_id"]

        assert log_timeline_pattern["#/log_type"] == ["event_log"]

        assert log_events_pattern["request_params/log_id"] == [1]
        assert log_events_pattern["#/log_id"] == [1]
        assert log_events_pattern["#/log_type"] == ["time_log"]
