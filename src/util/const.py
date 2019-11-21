class HTTPMethodKey:
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"

    DEFAULT = "DEFAULT"


class SchemaKey:
    REQUEST_METHOD = "request_method"
    REQUEST_PARAMS = "request_params"
    RESPONSE_DATA = "response_data"

    PATH = "path"
    TYPE = "type"
    POSSIBLE_TYPES = "possible_types"
    ARRAY_LENGTH_RANGE = "array_length_range"

    PROPERTIES = "properties"
    ITEMS = "items"
    REQUIRED = "required"
    EXAMPLE = "example"


class TypeKey:
    OBJECT = "object"
    ARRAY = "array"
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"  # 浮点数
    BOOLEAN = "boolean"
    NULL = "null"

    BASIC_TYPE = [STRING, INTEGER, NUMBER, BOOLEAN]


class PathKey:
    ROOT_PATH = "#"
    SPACE = "/"


class LoggingMessage:
    DataInFileInvalid = "data in the file is not valid json"


class TypeToTypeKeyMap:
    def __init__(self):

        self.type_map = {
            dict: TypeKey.OBJECT,
            list: TypeKey.ARRAY,
            str: TypeKey.STRING,
            int: TypeKey.INTEGER,
            float: TypeKey.NUMBER,
            bool: TypeKey.BOOLEAN,
            # None: TypeKey.NULL,
        }

    def get_key_map(self):
        return self.type_map


class RecordMapKey:
    ROOT = "root"
    COUNT = "count"
    TYPE_LIST = "types"
    VALUE_COUNT = "value_count"
    VALUE_IN = "value_in"
    KEY_EXIST_WHEN = "key_exist_when"

    ARRAY_ITEM_TYPE = "array_items_type"
    ARRAY_LENGTH_MIN = "array_length_min"
    ARRAY_LENGTH_MAX = "array_length_max"


