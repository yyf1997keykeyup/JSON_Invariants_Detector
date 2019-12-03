# coding=utf-8
import unittest
import json
import time

from src.util.const import HTTPMethodKey
from src.record_map.record_map import RecordMap
from src.converter.schema_generator import SchemaGenerator
from src.util.common import print_to_file


class TestValueIn(unittest.TestCase):
    def setUp(self):
        self.schema_generator = SchemaGenerator()
        self.record_map = RecordMap()

    def test_two_data(self):
        """
        pattern 1
        have 2 json data
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 99
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)
        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)

        self.record_map.load()

        """print to file"""
        # json_str = json.dumps(self.record_map.get_records(), indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/record.txt")

        invariant_schema = self.record_map.generate_invariant_schema()

        """print to file"""
        # json_str = json.dumps(invariant_schema, indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/invariant_schema.txt")

        target_path = invariant_schema["properties"]["data"]["possible_types"]["object"]["properties"][
            "grade"]["possible_types"]["integer"]

        assert "value_in" in target_path
        assert target_path["value_in"] == [60, 99]

    def test_puplicated_data(self):
        """
        pattern 1
        have 3 json data
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 99
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)

        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)

        schema_3 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Tyler"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_3)

        self.record_map.load()

        """print to file"""
        # json_str = json.dumps(self.record_map.get_records(), indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/record.txt")

        invariant_schema = self.record_map.generate_invariant_schema()

        """print to file"""
        # json_str = json.dumps(invariant_schema, indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/invariant_schema.txt")

        target_path = invariant_schema["properties"]["data"]["possible_types"]["object"]["properties"][
            "grade"]["possible_types"]["integer"]

        assert "value_in" in target_path
        assert target_path["value_in"] == [60, 99]

    def test_excessive_range(self):
        """
        pattern 1
        test when the potential of value is more than param--"value_in_max"
        have 5 json data
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 99
            }
        }
        data_3 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 100
            }
        }
        data_4 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 0
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)

        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)

        schema_3 = self.schema_generator.generate(json_dict=data_3,
                                                  request_params={"name": "John"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_3)

        schema_4 = self.schema_generator.generate(json_dict=data_4,
                                                  request_params={"name": "Jason"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_4)

        self.record_map.load()

        """print to file"""
        # json_str = json.dumps(self.record_map.get_records(), indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/record.txt")

        invariant_schema = self.record_map.generate_invariant_schema(value_in_max=3)

        """print to file"""
        # json_str = json.dumps(invariant_schema, indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/invariant_schema.txt")

        target_path = invariant_schema["properties"]["data"]["possible_types"]["object"]["properties"][
            "grade"]["possible_types"]["integer"]

        assert "value_in" in target_path
        assert len(target_path["value_in"]) == 0

    def test_same_monitor(self):
        """
        pattern 1
        test monitor function for the same input
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)
        self.record_map.load()

        invariant_schema = self.record_map.generate_invariant_schema()

        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)
        self.record_map.load()

        invariant_schema_changed = self.record_map.generate_invariant_schema()

        assert invariant_schema == invariant_schema_changed


    def test_diff_monitor(self):
        """
        pattern 1
        test monitor function for the different input
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 90
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)
        self.record_map.load()

        invariant_schema = self.record_map.generate_invariant_schema()

        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)
        self.record_map.load()

        invariant_schema_changed = self.record_map.generate_invariant_schema()

        # todo: give diff info
        assert invariant_schema != invariant_schema_changed

    # todo: seperate the below apart

    def test_possible_type(self):
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



