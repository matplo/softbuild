#!/usr/bin/env python

import pyutils
import os

packages_paths = {}

import configparser
import cfgutil
import argparse

class BuildSetup(object):
    def __init__(self, args):
        print(agrs)

def get_fastjet_configuration():
    fname = os.path.join(pyutils.heppy_dir(), 'cppyy/config/fastjet.cfg')
    cfg = configparser.ConfigParser()
    cfg.read(fname)
    print(cfg.sections())
    for s in cfg.sections():
        print(s)
        for key in cfg[s]:
            # make sure to replace the ${} with actual key values!
            print('   ', key, '=', cfg[s][key])
            # print(' ', key, '=', cfgutil.process_substring_in_config(cfg[s][key], cfg[s]))            
            print(' ->', key, '=', cfgutil.process_property_in_config(cfg[s][key], cfg[s]))            


def get_this_directory():
    return os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', help='prefix of the installation {}'.format(get_this_directory()), default=get_this_directory())
    args = parser.parse_args()

    build_cfg = cfgutil.BuildConfig()
    fj_cfg = cfgutil.BuildConfig(name='fastjet', version='3.3.3', build_cfg=build_cfg)
    print(fj_cfg)
    fj_cfg.build()


if __name__=="__main__":
    main()
