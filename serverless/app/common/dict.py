def get_striped(vals, key, def_val=''):
    val = vals.get(key, '').strip()
    if len(val) == 0:
        val = def_val
    return val


def keys_from_dicts(dicts, key):
    tmp = {}
    for i in dicts:
        k = i[key]
        tmp[k] = 1
    return list(tmp.keys())


def check_same_dicts(dict_a, dict_b, ignore_keys=[]):
    filtered_a = {k: v for k, v in dict_a.items() if k not in ignore_keys}
    filtered_b = {k: v for k, v in dict_b.items() if k not in ignore_keys}
    return filtered_a == filtered_b
