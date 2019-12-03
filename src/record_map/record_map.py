import sys
from src.util.const import SchemaKey, TypeKey, RecordMapKey, PathKey


class RecordMap:
    def __init__(self):
        self.json_schema_list = []
        self.path2records = {}
        self.context_dict = {}
        self.covered_path = set()

    def get_records(self):
        return self.path2records

    def add(self, schema: dict):
        self.json_schema_list.append(schema)

    def load(self):
        """
        todo: add a schema, update the records
        :return:
        """
        self.pre_process()
        for schema in self.json_schema_list:
            self.context_dict = dict()
            self.covered_path = set()
            self.set_layer_context(schema)
            response_data_dict = schema.get(SchemaKey.RESPONSE_DATA).get(SchemaKey.PROPERTIES)
            self.parse_dict(response_data_dict)
            self.set_uncovered_path()

    def pre_process(self):
        for schema in self.json_schema_list:
            response_data_dict = schema.get(SchemaKey.RESPONSE_DATA).get(SchemaKey.PROPERTIES)
            self.set_dict_path(response_data_dict)

    def set_dict_path(self, schema):
        for _, data_info in schema.items():
            path = data_info[SchemaKey.PATH]
            self.path2records[path] = self.init_path_record()
            if data_info[SchemaKey.TYPE] == TypeKey.OBJECT:
                self.set_dict_path(data_info[SchemaKey.PROPERTIES])
                    
    def init_path_record(self):
        path_record = {
            RecordMapKey.COUNT: 0,
            RecordMapKey.NOT_EXIST_WHEN: {},
            RecordMapKey.TYPE_LIST: {}
        }
        return path_record

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

        if SchemaKey.TYPE in response_data_dict:
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
            self.covered_path.add(path)

            # if path not in self.path2records:
            #     self.path2records[path] = self.init_path_record()

            self.path2records[path][RecordMapKey.COUNT] += 1

            if key_attrs[SchemaKey.TYPE] not in self.path2records[path][RecordMapKey.TYPE_LIST]:
                self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs[SchemaKey.TYPE]] = self.init_type_record()

            type_root = self.path2records[path][RecordMapKey.TYPE_LIST][key_attrs.get(SchemaKey.TYPE)]
            type_root[RecordMapKey.COUNT] += 1
            # 更新 context
            type_root[RecordMapKey.EXIST_WHEN] = self.add_or_update_context(path, type_root[RecordMapKey.EXIST_WHEN])

            # 更新基础类型的 VALUE_COUNT
            if key_attrs[SchemaKey.TYPE] in TypeKey.BASIC_TYPE:
                value = key_attrs[SchemaKey.EXAMPLE][0]
                type_root[RecordMapKey.VALUE_COUNT][value] = type_root[RecordMapKey.VALUE_COUNT].get(value, 0) + 1

            # 更新array类型的 属性 (array item type, max and min length of array)
            elif key_attrs[SchemaKey.TYPE] == TypeKey.ARRAY:
                if SchemaKey.TYPE in key_attrs[SchemaKey.ITEMS]:
                    type_root[RecordMapKey.ARRAY_ITEM_TYPE] = key_attrs[SchemaKey.ITEMS][SchemaKey.TYPE]
                    if SchemaKey.EXAMPLE in key_attrs[SchemaKey.ITEMS]:
                        type_root[RecordMapKey.ARRAY_LENGTH_MAX] = max(type_root.get(RecordMapKey.ARRAY_LENGTH_MAX, 0), len(key_attrs[SchemaKey.ITEMS][SchemaKey.EXAMPLE]))
                        type_root[RecordMapKey.ARRAY_LENGTH_MIN] = min(type_root.get(RecordMapKey.ARRAY_LENGTH_MIN, sys.maxsize), len(key_attrs[SchemaKey.ITEMS][SchemaKey.EXAMPLE]))

            elif key_attrs[SchemaKey.TYPE] == TypeKey.OBJECT:
                self.parse_dict(key_attrs[SchemaKey.PROPERTIES])

    def init_type_record(self):
        type_record = {
            RecordMapKey.COUNT: 0,
            RecordMapKey.VALUE_COUNT: {},
            RecordMapKey.EXIST_WHEN: {}
        }
        return type_record

    # todo:
    def add_or_update_context(self, root_path: str, context):

        for key, value in self.context_dict[RecordMapKey.REQUEST].items():
            if key not in context:
                context[key] = []
            if value not in context[key]:
                context[key].append(value)

        root_path_list = root_path.split(PathKey.SPACE)[:-1]
        context_key = PathKey.ROOT_PATH
        self.set_contexts(root_path, context_key, context)

        for path_node in root_path_list[1:]:
            context_key += PathKey.SPACE + path_node
            self.set_contexts(root_path, context_key, context)

        return context

    def set_contexts(self, root_path, context_key, context):
        for key, value in self.context_dict[context_key].items():
            combined_key = context_key + PathKey.SPACE + key
            if combined_key != root_path:
                if combined_key not in context:
                    context[combined_key] = []
                if value not in context[combined_key]:
                    context[combined_key].append(value)

    def set_uncovered_path(self):
        for path, records in self.path2records.items():
            if path not in self.covered_path:
                if RecordMapKey.NOT_EXIST_WHEN not in records:
                    records[RecordMapKey.NOT_EXIST_WHEN] = {}
                records[RecordMapKey.NOT_EXIST_WHEN] = self.add_or_update_context(path, records[RecordMapKey.NOT_EXIST_WHEN])

    def generate_invariant_schema(self, value_in_max=10) -> dict:
        """
        value_in_max: the max length of "value_in" pattern
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
                    key_addr = key_addr[key_root_path][SchemaKey.POSSIBLE_TYPES][TypeKey.OBJECT][SchemaKey.PROPERTIES]

            not_exist_when = key_records[RecordMapKey.NOT_EXIST_WHEN]
            possible_types = {}
            key_addr[key_name] = {
                SchemaKey.PATH: key_path,
                SchemaKey.NOT_EXIST_WHEN: not_exist_when,
                SchemaKey.POSSIBLE_TYPES: possible_types,
            }
            self.set_not_exist_when(not_exist_when, key_records)

            type2precondition = self.get_pre_condition(key_records)

            for type_name, type_records in key_records[RecordMapKey.TYPE_LIST].items():
                type_info = {}
                possible_types[type_name] = type_info

                # todo: actual condition: Basic type
                if RecordMapKey.VALUE_COUNT in type_records:
                    if len(type_records[RecordMapKey.VALUE_COUNT].keys()) <= value_in_max:
                        type_info[RecordMapKey.VALUE_IN] = list(type_records[RecordMapKey.VALUE_COUNT].keys())
                    else:
                        type_info[RecordMapKey.VALUE_IN] = []
                    # todo: test, refine it later
                    type_info[SchemaKey.PRE_CONDITION] = type2precondition.get(type_name, {})

                if type_name == TypeKey.ARRAY:
                    type_info[RecordMapKey.ARRAY_ITEM_TYPE] = type_records.get(RecordMapKey.ARRAY_ITEM_TYPE)
                    if RecordMapKey.ARRAY_LENGTH_MIN in type_records:
                        type_info[SchemaKey.ARRAY_LENGTH_RANGE] = \
                            [type_records[RecordMapKey.ARRAY_LENGTH_MIN], type_records[RecordMapKey.ARRAY_LENGTH_MAX]]

                if type_name == TypeKey.OBJECT:
                    type_info[SchemaKey.PROPERTIES] = {}

        return _invariant_schema

    def set_not_exist_when(self, not_exist_when, key_records):
        for _, type_records in key_records[RecordMapKey.TYPE_LIST].items():
            exist_when = type_records[RecordMapKey.EXIST_WHEN]
            for path, val_list in exist_when.items():
                if path in not_exist_when:
                    for val in val_list:
                        if (val in not_exist_when[path]):
                            not_exist_when[path].remove(val)
                    if len(not_exist_when[path]) == 0:
                        not_exist_when.pop(path)

    def get_pre_condition(self, key_records):
        type2precondition = {}
        if len(key_records[RecordMapKey.TYPE_LIST]) == 1:
            return type2precondition

        param_dict = self.get_param_dict(key_records)
        for param_name, val2type in param_dict.items():
            for val, type_set in val2type.items():
                if len(type_set) == 1:
                    _type = type_set.pop()

                    if _type not in type2precondition:
                        type2precondition[_type] = {}
                    type2precondition[_type][param_name] = val

        return type2precondition

    def get_param_dict(self, key_records):
        param_dict = {}
        for type_name, type_records in key_records[RecordMapKey.TYPE_LIST].items():
            context_dict = type_records[RecordMapKey.EXIST_WHEN]
            for param_name, param_val_list in context_dict.items():

                if param_name not in param_dict:
                    param_dict[param_name] = {}

                for param_val in param_val_list:
                    if param_val not in param_dict[param_name]:
                        param_dict[param_name][param_val] = set()

                    param_dict[param_name][param_val].add(type_name)

        return param_dict
