import os
import configparser
import pprint


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


def get_this_directory():
    return os.path.dirname(os.path.abspath(__file__))


class BuildConfig(object):
    def __init__(self, input_file=None, name=None, version=None, directory=None, build_cfg=None):
        self.version = version
        self.directory = directory
        if self.directory is None:
            self.directory = os.path.join(get_this_directory(), 'configs')
        self.input_file = input_file
        self.name = name
        if self.name is None:
            self.name = 'build'
        if self.input_file is None:
            self.input_file = os.path.join(self.directory, self.name + '.cfg')
        self.cfg = None
        if os.path.exists(self.input_file):
            self.cfg = configparser.ConfigParser()
            self.cfg.read(self.input_file)
        self.settings = {}
        self.settings['name'] = self.name
        self.settings['input_file'] = self.input_file
        self.settings['version'] = version
        self.settings['directory'] = self.directory
        self.settings['cfg_read'] = False

        if build_cfg:
            for s in self.cfg.sections():
                if s == self.version or self.version is None:
                    self.cfg.set(s, 'install_prefix', os.path.join(build_cfg.settings['install_prefix'], self.cfg[s]['install_prefix']))

        if self.cfg:
            for s in self.cfg.sections():
                if s == self.version or self.version is None:
                    for key in self.cfg[s]:
                        self.settings[key] = process_property_in_config(self.cfg[s][key], self.cfg[s])
                        # self.settings[key] = self.cfg[s][key]
                    self.settings['cfg_read'] = True
                    self.settings['version'] = s

        if build_cfg:
            for key in build_cfg.settings:
                if key in self.settings:
                    pass
                else:
                    self.settings[key] = build_cfg.settings[key]

                    
    def __repr__(self):
        s = ' '.join(['[i] Build Config',self.name, '\n'])
        s += ''.join(pprint.pformat(self.__dict__, indent=2))
        return s
                
    def build(self):
        build_script = os.path.join(self.settings['working_dir'], '{}-{}-build.sh'.format(self.name, self.version))
        os.makedirs(self.settings['working_dir'], exist_ok = True)
        with open(build_script, 'w') as f:
            print('#download', file=f)
            print('mkdir -p {}'.format(self.settings['download_dir']), file=f)
            print('cd {}'.format(self.settings['download_dir']), file=f)
            print('{}'.format(self.settings['download_cmnd']), file=f)

