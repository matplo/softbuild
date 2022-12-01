def min_dist(ref, vals):
    _dmin = 1e6
    _rv = -1
    for v in vals:
        if _dmin > v - ref:
            _dmin = v - ref
            _rv = v
    return _rv

def count_brackets(s):
    _bopen = []
    _bclose = []
    for i, c in enumerate(s):
        if c == '{':
            _bopen.append(i)
        if c == '}':
            _bclose.append(i)
    return _bopen, _bclose    

max_depth = 3
def process_substring_in_config(s, cfg_section, depth=0):
    if depth >= max_depth:
        print('[w] stopping processing string [{}] the string at depth'.format(s), depth)
        return s
    # learn how to parse a string with multiple matching brackets
    _bopen, _bclose = count_brackets(s)
    if len(_bopen) < 1:
        return s
    if len(_bopen) != len(_bclose):
        print('[i] syntax error: brackets not closing?')
        return None
    if len(_bopen) > 1:
        _substr = s[_bopen[1]:min_dist(_bopen[1], _bclose)+1]
        # print('replacing', _substr)
        s = s.replace(_substr, process_substring_in_config(_substr, cfg_section, depth+1))
    _substr = s[_bopen[0]:min_dist(_bopen[0], _bclose)+1]
    _substr_name = s[_bopen[0]+1:min_dist(_bopen[0], _bclose)]
    if cfg_section:
        s = s.replace(_substr, cfg_section[_substr_name])
    return s

def process_property_in_config(s, cfg_section):
    sret = s
    while True:
        _bopen, _bclose = count_brackets(sret)
        if len(_bopen) > 0:
            sret = process_substring_in_config(sret, cfg_section, 0)
        else:
            break
    return sret
