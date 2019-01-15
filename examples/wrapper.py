import json

def main(value):
    data = value
    if data == '':
        ret = {'empty': ''}
    else:
        try:
            current = json.loads(data)
        except Exception:
            current = data
        wrapped = {'wrapped': current}
    ret = json.dumps(wrapped)
    return ret