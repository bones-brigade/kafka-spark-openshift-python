import json

def user_defined_function(value):
    """Return a string-based JSON object

    This function accepts a string value and will return a string containing
    a JSON object. The returned object simply take the input string and
    puts it into a JSON object with the key `wrapped`.

    User defined functions must accept a single value (a string) and return
    either a string value or None. If None is returned there will be no
    message passed along the stream topic.
    """
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
