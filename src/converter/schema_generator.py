import json
import logging

from src.converter.const import SchemaKey, TypeKey, LoggingMessage, TypeToTypeKeyMap


class SchemaGenerator:
    def __init__(self):
        self.type_key_map = TypeToTypeKeyMap().get_key_map()

    def generate(self, file_path: str):
        json_dict = self.load_data_from_file(file_path)
        json_schema = self.init_json_schema()
        json_schema[SchemaKey.PROPERTIES] = self.parse_dict_properties(json_dict)

        json_str = json.dumps(json_schema, indent=4)
        self.print_to_file(json_str)
        return json_str

    def parse_dict_properties(self, json_dict: dict) -> dict:
        properties = {}
        for key, value in json_dict.items():
            type_key = TypeKey.NULL if value is None else self.type_key_map[type(value)]
            properties[key] = {SchemaKey.TYPE: type_key}
            if type(value) == dict:
                properties[key][SchemaKey.PROPERTIES] = self.parse_dict_properties(value)

        return properties

    def load_data_from_file(self, file_path: str) -> dict:
        with open(file_path, 'r') as f:
            data = f.read()
        try:
            loaded_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            logging.warning(LoggingMessage.DataInFileInvalid)
            loaded_data = {}

        return loaded_data

    def init_json_schema(self):
        initial_json_schema = {
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
