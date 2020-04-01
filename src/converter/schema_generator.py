import json

from util.common import load_data_from_file, print_to_file
from util.const import HTTPMethodKey, SchemaKey, TypeKey, TypeToTypeKeyMap, PathKey


class SchemaGenerator:
    def __init__(self):
        self.type_key_map = TypeToTypeKeyMap().get_key_map()

    def generate(self, json_dict: dict, request_params: dict, http_method=HTTPMethodKey.DEFAULT):
        json_schema = self.init_root_schema(request_params, http_method)
        json_schema[SchemaKey.RESPONSE_DATA][SchemaKey.PROPERTIES] = \
            self.parse_dict_properties(json_dict, json_schema[SchemaKey.RESPONSE_DATA][SchemaKey.PATH])

        json_str = json.dumps(json_schema, indent=4)
        # print_to_file(json_str)
        return json_schema

    def parse_dict_properties(self, json_dict: dict, root_path: str) -> dict:
        properties = {}
        for key, value in json_dict.items():
            type_key = TypeKey.NULL if value is None else self.type_key_map[type(value)]
            properties[key] = {
                SchemaKey.TYPE: type_key,
                SchemaKey.PATH: root_path + PathKey.SPACE + key,
            }
            if type(value) == dict:
                curr_path = root_path + PathKey.SPACE + key
                properties[key][SchemaKey.PROPERTIES] = self.parse_dict_properties(value, curr_path)
            elif type(value) == list:
                curr_path = root_path + PathKey.SPACE + key + PathKey.SPACE + SchemaKey.ITEMS
                properties[key][SchemaKey.ITEMS] = self.parse_list_item(value, curr_path)
                # properties[key][SchemaKey.EXAMPLE] = value
            else:
                # basic types
                properties[key][SchemaKey.EXAMPLE] = value,

        return properties

    def parse_list_item(self, json_list: list, curr_path: str) -> dict:
        if len(json_list) == 0:
            return {}
        # take the first one for example
        example_item = json_list[0]
        items = {
            SchemaKey.TYPE: TypeKey.NULL if example_item is None else self.type_key_map[type(example_item)],
            SchemaKey.PATH: curr_path,
        }
        if items[SchemaKey.TYPE] in TypeKey.BASIC_TYPE:
            items[SchemaKey.EXAMPLE] = json_list
        elif items[SchemaKey.TYPE] == TypeKey.ARRAY:
            items[SchemaKey.ITEMS] = self.parse_list_item(json_list[0], curr_path)
        elif items[SchemaKey.TYPE] == TypeKey.OBJECT:
            items[SchemaKey.PROPERTIES] = self.parse_dict_properties(json_list[0], curr_path)

        return items

    def init_root_schema(self, request_params: dict, http_method: str):
        initial_root_schema = {
            SchemaKey.REQUEST_METHOD: http_method,
            SchemaKey.REQUEST_PARAMS: request_params,
            SchemaKey.RESPONSE_DATA: self.init_response_data_schema(),
        }
        return initial_root_schema

    def init_response_data_schema(self):
        initial_json_schema = {
            SchemaKey.PATH: PathKey.ROOT_PATH,
            SchemaKey.TYPE: TypeKey.OBJECT,
            SchemaKey.PROPERTIES: {},
        }
        return initial_json_schema
