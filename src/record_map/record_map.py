import json
import sys

from src.converter.schema_generator import SchemaGenerator
from src.util.common import print_to_file
from src.util.const import SchemaKey, TypeKey, RecordMapKey, HTTPMethodKey, PathKey


class RecordMap:
    def __init__(self):
        self.path2records = {}

    def add(self, schema: dict):
        """
        todo: add a schema, update the records
        :param schema:
        :return:
        """
        request_method = schema.get(SchemaKey.REQUEST_METHOD)
        request_params = schema.get(SchemaKey.REQUEST_PARAMS)
        response_data_dict = schema.get(SchemaKey.RESPONSE_DATA).get(SchemaKey.PROPERTIES)
        root = schema.get(SchemaKey.RESPONSE_DATA).get(SchemaKey.PATH)
        self.parse_dict(response_data_dict, root)

    def parse_dict(self, data_dict: dict, root: str):
        for _, key_attrs in data_dict.items():
            path = key_attrs.get(SchemaKey.PATH)

            if path in self.path2records:
                # update
                self.path2records[path][RecordMapKey.COUNT] += 1
                if key_attrs[SchemaKey.TYPE] in self.path2records[path][RecordMapKey.TYPE_LIST]:
                    self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs[SchemaKey.TYPE]][RecordMapKey.COUNT] += 1
                    if key_attrs[SchemaKey.TYPE] in TypeKey.BASIC_TYPE:
                        value = key_attrs[SchemaKey.EXAMPLE][0]
                        value_count = self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)][RecordMapKey.VALUE_COUNT]
                        self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)][RecordMapKey.VALUE_COUNT][value] = value_count.get(value, 0) + 1
                else:
                    self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs[SchemaKey.TYPE]] = {
                        RecordMapKey.COUNT: 1,
                        # RecordMapKey.KEY_EXIST_WHEN: {}
                    }
            else:
                # init
                self.path2records[path] = self.init_records(key_attrs, root)

            if key_attrs[SchemaKey.TYPE] == TypeKey.OBJECT:
                self.parse_dict(key_attrs[SchemaKey.PROPERTIES], path)

    def init_records(self, key_attrs: dict, root: str) -> dict:
        records = {
            RecordMapKey.ROOT: root,
            RecordMapKey.COUNT: 1,
            RecordMapKey.TYPE_LIST: {}
        }
        records[RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)] = {
            RecordMapKey.COUNT: 1,
            # RecordMapKey.KEY_EXIST_WHEN: {}
        }
        if key_attrs[SchemaKey.TYPE] in TypeKey.BASIC_TYPE:
            value = key_attrs[SchemaKey.EXAMPLE][0]
            records[RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)][RecordMapKey.VALUE_COUNT] = {value: 1}
        elif key_attrs[SchemaKey.TYPE] == TypeKey.ARRAY:
            # when it is an array
            records[RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)][RecordMapKey.ARRAY_ITEM_TYPE] \
                = key_attrs[SchemaKey.ITEMS][SchemaKey.TYPE]
            records[RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)][RecordMapKey.ARRAY_LENGTH_MAX] \
                = max(records[RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)].get(RecordMapKey.ARRAY_LENGTH_MAX, 0), len(key_attrs[SchemaKey.EXAMPLE]))
            records[RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)][RecordMapKey.ARRAY_LENGTH_MIN] \
                = min(records[RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)].get(RecordMapKey.ARRAY_LENGTH_MIN, sys.maxsize), len(key_attrs[SchemaKey.EXAMPLE]))

        return records

    def generate_invariant_schema(self) -> dict:
        """
        todo: generate invariant schema, data comes from records
        :return:
        """
        property_dict = {}
        _invariant_schema = {
            SchemaKey.PATH: PathKey.ROOT_PATH,
            SchemaKey.TYPE: TypeKey.OBJECT,
            SchemaKey.PROPERTIES: property_dict,
        }
        for key_path, key_records in self.path2records.items():
            key_name = key_path.split(PathKey.SPACE)[-1]
            key_root_paths = key_path.split(PathKey.SPACE)[:-1]
            key_addr = property_dict
            for key_root_path in key_root_paths:
                if key_root_path != PathKey.ROOT_PATH:
                    key_addr = property_dict[key_root_path][SchemaKey.POSSIBLE_TYPES][TypeKey.OBJECT]

            possible_types = {}
            key_addr[key_name] = {
                SchemaKey.PATH: key_path,
                SchemaKey.POSSIBLE_TYPES: possible_types
            }
            for type_name, type_records in key_records[RecordMapKey.TYPE_LIST].items():
                possible_types[type_name] = dict()
                type_info = possible_types[type_name]

                if RecordMapKey.VALUE_COUNT in type_records:
                    type_info[RecordMapKey.VALUE_IN] = list(type_records[RecordMapKey.VALUE_COUNT].keys())

                if type_name == TypeKey.ARRAY:
                    type_info[SchemaKey.ARRAY_LENGTH_RANGE] = [type_records[RecordMapKey.ARRAY_LENGTH_MIN], type_records[RecordMapKey.ARRAY_LENGTH_MAX]]
                    type_info[RecordMapKey.ARRAY_ITEM_TYPE] = type_records[RecordMapKey.ARRAY_ITEM_TYPE]

        return _invariant_schema


def test_pattern1():
    sg = SchemaGenerator()
    rm = RecordMap()
    schema = sg.generate(file_path="../../testcases/pattern1/data1.txt",
                         request_params={},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    schema = sg.generate(file_path="../../testcases/pattern1/data2.txt",
                         request_params={},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    json_str = json.dumps(rm.path2records, indent=4)
    print_to_file(json_str, file_name="../../output/record.txt")

    invariant_schema = rm.generate_invariant_schema()
    json_str = json.dumps(invariant_schema, indent=4)
    print_to_file(json_str, file_name="../../output/invariant_schema.txt")


def test_pattern2():
    sg = SchemaGenerator()
    rm = RecordMap()
    schema = sg.generate(file_path="../../testcases/pattern2/data1.txt",
                         request_params={"param": "name"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    schema = sg.generate(file_path="../../testcases/pattern2/data2.txt",
                         request_params={"param": "skills"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    json_str = json.dumps(rm.path2records, indent=4)
    print_to_file(json_str, file_name="../../output/pattern2/record.txt")

    invariant_schema = rm.generate_invariant_schema()
    json_str = json.dumps(invariant_schema, indent=4)
    print_to_file(json_str, file_name="../../output/pattern2/invariant_schema.txt")


if __name__ == "__main__":
    # test_pattern1()
    # test_pattern2()
    sg = SchemaGenerator()
    rm = RecordMap()
    schema = sg.generate(file_path="../../testcases/pattern3/data1.txt",
                         request_params={"param": "name"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    json_str = json.dumps(rm.path2records, indent=4)
    print_to_file(json_str, file_name="../../output/pattern3/record.txt")

    invariant_schema = rm.generate_invariant_schema()
    json_str = json.dumps(invariant_schema, indent=4)
    print_to_file(json_str, file_name="../../output/pattern3/invariant_schema.txt")