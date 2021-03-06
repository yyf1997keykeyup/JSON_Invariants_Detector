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

    def test_two_data(self):
        """
        pattern 2
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "id": 434,
                "name": "John",
                "role": "student"
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": [434, 343, 93]
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "John"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)
        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"role": "student"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)

        self.record_map.load()

        """print to file"""
        # json_str = json.dumps(self.record_map.get_records(), indent=4)
        # print_to_file(json_str, file_name="../../output/pattern2/record.txt")

        invariant_schema = self.record_map.generate_invariant_schema()

        """print to file"""
        # json_str = json.dumps(invariant_schema, indent=4)
        # print_to_file(json_str, file_name="../../output/pattern2/invariant_schema.txt")

        target_path = invariant_schema["properties"]["data"]["possible_types"]

        assert len(target_path) == 2
        assert "object" in target_path
        assert target_path["object"]["pre_condition"] == {'request_params/name': 'John'}
        assert "array" in target_path
        assert target_path["array"]["pre_condition"] == {'request_params/role': 'student'}
