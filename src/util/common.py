import json
import logging

from util.const import LoggingMessage


def load_data_from_file(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        data = f.read()
    try:
        loaded_data = json.loads(data)
    except json.decoder.JSONDecodeError:
        logging.warning(LoggingMessage.DataInFileInvalid)
        loaded_data = {}

    return loaded_data


def print_to_file(_schema: str, file_name="../../output/a.txt"):
    with open(file_name, 'w') as the_file:
        the_file.write(_schema)
