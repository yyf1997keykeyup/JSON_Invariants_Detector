import json
from src.converter.schema_generator import SchemaGenerator
from src.record_map.record_map import RecordMap
from src.util.const import HTTPMethodKey
from src.util.common import print_to_file, load_data_from_file


#  todo: [alert] this test file is the old version.
#   please go to the "test" directory to run unit tests.

def test_pattern1():
    sg = SchemaGenerator()
    rm = RecordMap()
    json_dict = load_data_from_file("../../testcases/pattern1/data1.txt")
    schema = sg.generate(json_dict=json_dict,
                         request_params={"name": "Yufeng"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    json_dict = load_data_from_file("../../testcases/pattern1/data1.txt")
    schema = sg.generate(json_dict=json_dict,
                         request_params={"name": "Yinuo"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    rm.load()
    json_str = json.dumps(rm.path2records, indent=4)
    print_to_file(json_str, file_name="../../output/pattern1/record.txt")

    invariant_schema = rm.generate_invariant_schema()
    json_str = json.dumps(invariant_schema, indent=4)
    print_to_file(json_str, file_name="../../output/pattern1/invariant_schema.txt")


def test_pattern2():
    sg = SchemaGenerator()
    rm = RecordMap()
    json_dict = load_data_from_file("../../testcases/pattern2/data1.txt")
    schema = sg.generate(json_dict=json_dict,
                         request_params={"name": "John"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    json_dict = load_data_from_file("../../testcases/pattern2/data2.txt")
    schema = sg.generate(json_dict=json_dict,
                         request_params={"role": "student"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    rm.load()
    json_str = json.dumps(rm.path2records, indent=4)
    print_to_file(json_str, file_name="../../output/pattern2/record.txt")

    invariant_schema = rm.generate_invariant_schema()
    json_str = json.dumps(invariant_schema, indent=4)
    print_to_file(json_str, file_name="../../output/pattern2/invariant_schema.txt")


def test_pattern3():
    sg = SchemaGenerator()
    rm = RecordMap()
    json_dict = load_data_from_file("../../testcases/pattern3/data1.txt")
    schema = sg.generate(json_dict=json_dict,
                         request_params={"log_id": 1},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    json_dict = load_data_from_file("../../testcases/pattern3/data2.txt")
    schema = sg.generate(json_dict=json_dict,
                         request_params={"log_id": 9},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    rm.load()
    json_str = json.dumps(rm.path2records, indent=4)
    print_to_file(json_str, file_name="../../output/pattern3/record.txt")

    invariant_schema = rm.generate_invariant_schema()
    json_str = json.dumps(invariant_schema, indent=4)
    print_to_file(json_str, file_name="../../output/pattern3/invariant_schema.txt")


def test_pattern4():
    sg = SchemaGenerator()
    rm = RecordMap()
    json_dict = load_data_from_file("../../testcases/pattern4/data1.txt")
    schema = sg.generate(json_dict=json_dict,
                         request_params={"param": "v1"},
                         http_method=HTTPMethodKey.GET)
    rm.add(schema)
    rm.load()
    json_str = json.dumps(rm.path2records, indent=4)
    print_to_file(json_str, file_name="../../output/pattern4/record.txt")

    invariant_schema = rm.generate_invariant_schema()
    json_str = json.dumps(invariant_schema, indent=4)
    print_to_file(json_str, file_name="../../output/pattern4/invariant_schema.txt")


if __name__ == "__main__":
    # test_pattern1()
    test_pattern2()
    test_pattern3()
    test_pattern4()
