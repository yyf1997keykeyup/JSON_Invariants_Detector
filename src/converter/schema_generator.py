import json
import logging

from src.converter.const import SchemaKey, TypeKey, LoggingMessage, TypeToTypeKeyMap, PathKey


class SchemaGenerator:
    def __init__(self):
        self.type_key_map = TypeToTypeKeyMap().get_key_map()

    def generate(self, file_path: str):
        json_dict = self.load_data_from_file(file_path)
        json_schema = self.init_root_schema()
        json_schema[SchemaKey.PROPERTIES] = self.parse_dict_properties(json_dict, json_schema[SchemaKey.PATH])

        json_str = json.dumps(json_schema, indent=4)
        self.print_to_file(json_str)
        return json_str

    def parse_dict_properties(self, json_dict: dict, root_path: str) -> dict:
        properties = {}
        for key, value in json_dict.items():
            type_key = TypeKey.NULL if value is None else self.type_key_map[type(value)]
            properties[key] = {
                SchemaKey.TYPE: type_key,
                SchemaKey.PATH: root_path + PathKey.SPACE + SchemaKey.PROPERTIES + PathKey.SPACE + key,
                SchemaKey.EXAMPLE: value,
            }
            if type(value) == dict:
                curr_path = root_path + PathKey.SPACE + SchemaKey.PROPERTIES + PathKey.SPACE + key
                properties[key][SchemaKey.PROPERTIES] = self.parse_dict_properties(value, curr_path)
            elif type(value) == list:
                properties[key][SchemaKey.ITEMS] = self.parse_list_item(value)
                properties[key][SchemaKey.EXAMPLE] = value

        return properties

    def parse_list_item(self, json_list: list) -> dict:
        items = {}
        for item in json_list:
            items[SchemaKey.TYPE] = TypeKey.NULL if item is None else self.type_key_map[type(item)]
        return items

    def load_data_from_file(self, file_path: str) -> dict:
        with open(file_path, 'r') as f:
            data = f.read()
        try:
            loaded_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            logging.warning(LoggingMessage.DataInFileInvalid)
            loaded_data = {}

        return loaded_data

    def init_root_schema(self):
        initial_json_schema = {
            SchemaKey.PATH: PathKey.ROOT_PATH,
            SchemaKey.TYPE: TypeKey.OBJECT,
            SchemaKey.PROPERTIES: {},
        }
        return initial_json_schema

    def print_to_file(self, _schema: str, file_name="../../output/a.txt"):
        with open(file_name, 'a') as the_file:
            the_file.write(_schema)


if __name__ == "__main__":
    sg = SchemaGenerator()
    schema = sg.generate("../../testcases/simple_case.txt")
    print(schema)
