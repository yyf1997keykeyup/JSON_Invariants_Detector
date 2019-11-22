import json
import sys

from src.converter.schema_generator import SchemaGenerator
from src.util.common import print_to_file
from src.util.const import SchemaKey, TypeKey, RecordMapKey, HTTPMethodKey, PathKey


class RecordMap:
    def __init__(self):
        self.path2records = {}
        self.context_dict = {}

    def add(self, schema: dict):
        """
        todo: add a schema, update the records
        :param schema:
        :return:
        """
        self.context_dict = dict()
        self.set_layer_context(schema)
        response_data_dict = schema.get(SchemaKey.RESPONSE_DATA).get(SchemaKey.PROPERTIES)
        # root_dict = schema.get(SchemaKey.RESPONSE_DATA)
        self.parse_dict(response_data_dict)

    def set_layer_context(self, _schema: dict):
        request_method = _schema.get(SchemaKey.REQUEST_METHOD)
        request_params = _schema.get(SchemaKey.REQUEST_PARAMS)
        response_data_dict = _schema.get(SchemaKey.RESPONSE_DATA).get(SchemaKey.PROPERTIES)

        self.set_root_context(request_method, request_params)
        self.set_response_data_context(response_data_dict, root_name=PathKey.ROOT_PATH)

    def set_root_context(self, request_method: str, request_params: dict):
        root_context_dict = dict()
        root_context_dict[SchemaKey.REQUEST_METHOD] = request_method

        for param_name, param_value in request_params.items():
            param_path = SchemaKey.REQUEST_PARAMS + PathKey.SPACE + param_name
            root_context_dict[param_path] = param_value

        self.context_dict[RecordMapKey.REQUEST] = root_context_dict

    def set_response_data_context(self, response_data_dict: dict, root_name: str):
        layer_context = dict()

        for data_key, data_info in response_data_dict.items():
            if data_info[SchemaKey.TYPE] in TypeKey.BASIC_TYPE:
                layer_context[data_key] = data_info[SchemaKey.EXAMPLE][0]
            elif data_info[SchemaKey.TYPE] == TypeKey.NULL:
                layer_context[data_key] = None
            elif data_info[SchemaKey.TYPE] == TypeKey.OBJECT:
                self.set_response_data_context(data_info[SchemaKey.PROPERTIES], data_info[SchemaKey.PATH])
            elif data_info[SchemaKey.TYPE] == TypeKey.ARRAY:
                self.set_array_item_context(data_info[SchemaKey.ITEMS], data_info[SchemaKey.PATH])

        self.context_dict[root_name] = layer_context

    def set_array_item_context(self, response_data_dict: dict, root_name: str):
        layer_context = dict()

        if response_data_dict[SchemaKey.TYPE] in TypeKey.BASIC_TYPE:
            layer_context[SchemaKey.ITEMS] = response_data_dict[SchemaKey.EXAMPLE]
        elif response_data_dict[SchemaKey.TYPE] == TypeKey.NULL:
            layer_context[SchemaKey.ITEMS] = None
        elif response_data_dict[SchemaKey.TYPE] == TypeKey.OBJECT:
            self.set_response_data_context(response_data_dict[SchemaKey.PROPERTIES], response_data_dict[SchemaKey.PATH])
        elif response_data_dict[SchemaKey.TYPE] == TypeKey.ARRAY:
            self.set_response_data_context(response_data_dict[SchemaKey.ITEMS], response_data_dict[SchemaKey.PATH])

        self.context_dict[root_name] = layer_context

    def parse_dict(self, data_dict: dict):
        for _, key_attrs in data_dict.items():
            path = key_attrs.get(SchemaKey.PATH)

            if path in self.path2records:
                # update
                self.path2records[path][RecordMapKey.COUNT] += 1
                if key_attrs[SchemaKey.TYPE] in self.path2records[path][RecordMapKey.TYPE_LIST]:
                    self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs[SchemaKey.TYPE]][RecordMapKey.COUNT] += 1
                    if key_attrs[SchemaKey.TYPE] in TypeKey.BASIC_TYPE:
                        value = key_attrs[SchemaKey.EXAMPLE][0]
                        value_count = self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)][
                            RecordMapKey.VALUE_COUNT]
                        value_count[value] = value_count.get(value, 0) + 1

                    self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs[SchemaKey.TYPE]][RecordMapKey.COMMON_CONTEXT] = self.add_or_update_context(path, self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs[SchemaKey.TYPE]][RecordMapKey.COMMON_CONTEXT])
                else:
                    self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs[SchemaKey.TYPE]] = {
                        RecordMapKey.COUNT: 1,
                        RecordMapKey.COMMON_CONTEXT: self.add_or_update_context(path)
                    }
            else:
                # init
                self.path2records[path] = self.init_records(key_attrs)

            if key_attrs[SchemaKey.TYPE] == TypeKey.OBJECT:
                self.parse_dict(key_attrs[SchemaKey.PROPERTIES])

    def init_records(self, key_attrs: dict) -> dict:
        records = {
            RecordMapKey.COUNT: 1,
            RecordMapKey.TYPE_LIST: {}
        }
        records[RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)] = {
            RecordMapKey.COUNT: 1,
            RecordMapKey.COMMON_CONTEXT: self.add_or_update_context(key_attrs.get(SchemaKey.PATH))
        }
        type_root = records[RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)]
        if key_attrs[SchemaKey.TYPE] in TypeKey.BASIC_TYPE:
            # basic type: store the pair of value and count
            value = key_attrs[SchemaKey.EXAMPLE][0]
            type_root[RecordMapKey.VALUE_COUNT] = {value: 1}
        elif key_attrs[SchemaKey.TYPE] == TypeKey.ARRAY:
            # when it is an array
            # set array item type, max and min length of array
            type_root[RecordMapKey.ARRAY_ITEM_TYPE] = key_attrs[SchemaKey.ITEMS][SchemaKey.TYPE]
            type_root[RecordMapKey.ARRAY_LENGTH_MAX] \
                = max(type_root.get(RecordMapKey.ARRAY_LENGTH_MAX, 0), len(key_attrs[SchemaKey.ITEMS][SchemaKey.EXAMPLE]))
            type_root[RecordMapKey.ARRAY_LENGTH_MIN] \
                = min(type_root.get(RecordMapKey.ARRAY_LENGTH_MIN, sys.maxsize), len(key_attrs[SchemaKey.ITEMS][SchemaKey.EXAMPLE]))

        return records

    # todo:
    def add_or_update_context(self, root_path: str, context=dict()):

        for key, value in self.context_dict[RecordMapKey.REQUEST].items():
            if key not in context:
                context[key] = []
            if value not in context[key]:
                context[key].append(value)

        root_path_list = root_path.split(PathKey.SPACE)[:-1]
        context_key = PathKey.ROOT_PATH
        for key, value in self.context_dict[context_key].items():
            combined_key = context_key + PathKey.SPACE + key
            if combined_key != root_path:
                if combined_key not in context:
                    context[combined_key] = []
                if value not in context[combined_key]:
                    context[combined_key].append(value)

        for path_node in root_path_list[1:]:
            context_key += PathKey.SPACE + path_node
            for key, value in self.context_dict[context_key].items():
                combined_key = context_key + PathKey.SPACE + key
                if combined_key != root_path:
                    if combined_key not in context:
                        context[combined_key] = []
                    if value not in context[combined_key]:
                        context[combined_key].append(value)

        return context

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
                    key_addr = key_addr[key_root_path][SchemaKey.POSSIBLE_TYPES][TypeKey.OBJECT]

            possible_types = {}
            key_addr[key_name] = {
                SchemaKey.PATH: key_path,
                SchemaKey.POSSIBLE_TYPES: possible_types,
            }
            for type_name, type_records in key_records[RecordMapKey.TYPE_LIST].items():
                possible_types[type_name] = dict()
                type_info = possible_types[type_name]

                if RecordMapKey.VALUE_COUNT in type_records:
                    type_info[RecordMapKey.VALUE_IN] = list(type_records[RecordMapKey.VALUE_COUNT].keys())
                    # todo: test, refine it later
                    type_info[RecordMapKey.COMMON_CONTEXT] = type_records[RecordMapKey.COMMON_CONTEXT],

                if type_name == TypeKey.ARRAY:
                    type_info[SchemaKey.ARRAY_LENGTH_RANGE] = [type_records[RecordMapKey.ARRAY_LENGTH_MIN],
                                                               type_records[RecordMapKey.ARRAY_LENGTH_MAX]]
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


def test_pattern3():
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


if __name__ == "__main__":
    # test_pattern1()
    # test_pattern2()
    # test_pattern3()
    sg = SchemaGenerator()
    rm = RecordMap()

    schema = sg.generate(file_path="../../testcases/simple_case.txt",
                         request_params={"param": "name"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)

    schema = sg.generate(file_path="../../testcases/simple_case_v2.txt",
                         request_params={"param": "name"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    json_str = json.dumps(rm.path2records, indent=4)
    print_to_file(json_str, file_name="../../output/record.txt")

    invariant_schema = rm.generate_invariant_schema()
    json_str = json.dumps(invariant_schema, indent=4)
    print_to_file(json_str, file_name="../../output/invariant_schema.txt")
