class SchemaKey:
    TYPE = "type"
    PROPERTIES = "properties"
    ITEMS = "items"
    REQUIRED = "required"
    OPTIONAL = "optional"


class TypeKey:
    OBJECT = "object"
    ARRAY = "array"
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"  # 浮点数
    BOOLEAN = "boolean"
    NULL = "null"


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
