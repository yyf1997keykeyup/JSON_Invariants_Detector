import json
from util.const import SchemaKey, TypeKey, LoggingMessage, TypeToTypeKeyMap


class SchemaComparator:
    def __init__(self):
        pass

    def compare(self, dic1: dict, dic2: dict, path1="#", path2="#"):
        for key in dic1:
            if key in dic2:
                # if none of them is basic
                if type(dic1[key]) != dict and type(dic2[key]) != dict:
                    if dic1[key] != dic2[key]:
                        # print Schema1
                        print("Schema1(path: ", end="")
                        print(path1 + "): ", end="")
                        print('"' + key + '"' + ": " + str(dic1[key]), end="")
                        print(";    ", end="")
                        # print Schema2
                        print("Schema2(path: ", end="")
                        print(path2 + "): ", end="")
                        print('"' + key + '"' + ": " + str(dic2[key]))
                elif type(dic1[key]) == dict and type(dic2[key]) == dict:
                    self.compare(dic1[key], dic2[key], str(path1+'/'+key), str(path2+'/'+key))
            else:
                print("Schema1(path: ", end="")
                print(path1 + "): ", end="")
                print('"' + key + '"' + ": " + str(dic1[key]), end="")
                print(";    ", end="")
                print("Schema2: no such key found")

        for key in dic2:
            if key not in dic1:
                print("Schema2(path: ", end="")
                print(path2 + "): ", end="")
                print('"' + key + '"' + ": " + str(dic2[key]), end="")
                print(";    ", end="")
                print("Schema1: no such key found")

    def compare_schema(self, schema1, schema2):
        with open(schema1, 'r') as f:
            schema1_dict = json.load(f)
        with open(schema2, 'r') as f:
            schema2_dict = json.load(f)
        self.compare(schema1_dict, schema2_dict)


if __name__ == "__main__":
    comparator = SchemaComparator()
    schema1 = '../../original_schema_example/schema_case_002'
    schema2 = '../../original_schema_example/schema_case_003'
    comparator.compare_schema(schema1, schema2)
