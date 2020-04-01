import getopt
import sys
import os

import json
from converter.schema_generator import SchemaGenerator
from record_map.record_map import RecordMap
from util.const import HTTPMethodKey
from util.common import print_to_file, load_data_from_file


guide_line = 'python ./src/main.py -i <input_folder> -o <output_folder> -x <extra_info_file>'


def main(argv):
    extra_file = ''
    input_folder = ''
    output_folder = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:x:")
    except getopt.GetoptError:
        print(guide_line)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(guide_line)
            sys.exit()
        elif opt == "-x":
            extra_file = arg
        elif opt == "-i":
            input_folder = arg
        elif opt == "-o":
            output_folder = arg

    extra_info_map = load_data_from_file(extra_file)

    run(input_folder, output_folder, extra_info_map)


def run(input_folder, output_folder, extra_info_map):
    sg = SchemaGenerator()
    rm = RecordMap()

    g = os.walk(input_folder)
    json_data_paths = []
    for path, dir_list, file_list in g:
        for file_name in file_list:
            if file_name in extra_info_map:
                json_data_paths.append(os.path.join(path, file_name))
                json_dict = load_data_from_file(os.path.join(path, file_name))
                schema = sg.generate(json_dict=json_dict,
                                     request_params=extra_info_map[file_name].get("params", dict()),
                                     http_method=extra_info_map[file_name].get("method", HTTPMethodKey.GET))
                rm.add(schema)

    rm.load()
    json_str = json.dumps(rm.path2records, indent=4)
    print_to_file(json_str, file_name=os.path.join(output_folder, "record_table.json"))

    invariant_schema = rm.generate_invariant_schema()
    json_str = json.dumps(invariant_schema, indent=4)
    print_to_file(json_str, file_name=os.path.join(output_folder, "invariant_schema.json"))


if __name__ == "__main__":
    main(sys.argv[1:])
