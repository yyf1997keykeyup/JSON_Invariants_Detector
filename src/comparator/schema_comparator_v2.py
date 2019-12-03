import json
from src.util.const import SchemaKey, TypeKey, LoggingMessage, TypeToTypeKeyMap
import logging

class SchemaComparator:
    def __init__(self):
        pass

    def eq(self, a, b, walked=None):

        walked = walked or {}
        if (id(a), id(b)) in walked:
            return True
        walked[(id(a), id(b))] = True
        for k in set(a) | set(b):
            if k not in a:
                logging.warning("%s not in %s", k, a)
                return False
            if k not in b:
                return False
            if not self.eq(a[k], b[k], walked):
                return False
        return True


if __name__ == "__main__":
    sc = SchemaComparator()
    print(sc.eq({}, {'x': {}}))  # False
    print(sc.eq({'x': {}}, {'x': {}}))  # True

    a = {}
    b = {}

    a['x'] = a

    b['x'] = {}
    b['x']['x'] = b
    print(sc.eq(a, b))  # True
