#!/usr/bin/env python

import pyutils
import os

packages_paths = {}

import configparser
import cfgutil

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


def main():
    heppy_dir = pyutils.heppy_dir()
    print('[i] heppy dir is at', heppy_dir)

    external_code_dir = os.path.join(heppy_dir, 'external')
    print('[i] external heppy dir is at', external_code_dir)

    packages_paths['fastjet'] = os.path.join(external_code_dir, 'fastjet/fastjet-current')
    fastjet_files = pyutils.find_files(packages_paths['fastjet'], '*.h')
    print(fastjet_files)

    get_fastjet_configuration()


if __name__=="__main__":
    main()