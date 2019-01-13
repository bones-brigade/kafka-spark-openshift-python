import json

def main(value):
    current = json.loads(value)
    wrapped = {'wrapped': current}
    ret = json.dumps(wrapped)
    return ret
