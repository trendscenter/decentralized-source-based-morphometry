import ujson as json
import numpy as np
import sys
from utils import listRecursive


def br_remote_noop(args):

    computation_output = {
        "output": {
            "computation_phase": "br_remote_noop"
        },
        "success": True
    }
    return json.dumps(computation_output)


if __name__ == '__main__':

    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(listRecursive(parsed_args, 'computation_phase'))

    if 'local_backreconstruct' in phase_key:
        computation_output = remote_noop(parsed_args)
        sys.stdout.write(computation_output)
    else:
        raise ValueError("Error occurred at Remote")
