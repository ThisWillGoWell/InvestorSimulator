
from json import dumps


def return_object_success(msg="", object=None):
    return {'status': 'success', 'msg': msg, 'object': object}


def return_object_error(msg):
    return {'status': 'error', 'msg': msg}


def map_num(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def success(result):
    if 'status' in result:
        return result['status'] == 'success'


def print_dict(d):
    print(dumps(d))
