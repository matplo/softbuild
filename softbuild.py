#!/usr/bin/env python3

import os
import argparse
import sys
import shlex
import subprocess
import re

def get_this_directory():
	return os.path.dirname(os.path.abspath(__file__))


class GenericObject(object):
	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			self.__setattr__(key, value)

	def configure_from_args(self, **kwargs):
		for key, value in kwargs.items():
			self.__setattr__(key, value)
   
	def configure_from_dict(self, d):
		for k in d:
			self.__setattr__(k, d[k])

	def __getattr__(self, key):
		try:
			return self.__dict__[key]
		except:
			pass
		self.__setattr__(key, None)
		return self.__getattr__(key)

	def __str__(self) -> str:
		s = []
		s.append('[i] {}'.format(str(self.__class__).split('.')[1].split('\'')[0]))
		for a in self.__dict__:
			if a[0] == '_':
				continue
			sval = str(getattr(self, a))
			if len(sval) > 200:
				sval = sval[:200]
			s.append('   {} = {}'.format(str(a), sval))
		return '\n'.join(s)

	def __repr__(self) -> str:
		return self.__str__()

	def __getitem__(self, key):
		return self.__getattr__(key)

	def __iter__(self):
		_props = [a for a in self.__dict__ if a[0] != '_']
		return iter(_props)


# return dictionary where a=value can be more words 23
def get_eq_val(s):
	ret_dict = {}
	if s is None:
		return ret_dict
	if len(s) < 1:
		return ret_dict
	regex = r"[\w]+="
	matches = re.findall(regex, s, re.MULTILINE)
	return matches
	for i, m in enumerate(matches):
		m_start = s.index(m)
		m_end = -1
		if i < len(matches) - 1:
			m_end = s.index(matches[i+1]) - 1
		else:
			m_end = len(s)
		_sm = s[m_start:m_end]
		eqs = _sm.split('=')
		ret_dict[eqs[0]] = eqs[1].strip()
	return ret_dict


class BuildScript(GenericObject):
	_download_cmnd = os.path.join(__file__)
	def __init__(self, **kwargs):
		super(BuildScript, self).__init__(**kwargs)
		if self.args:
			self.configure_from_dict(self.args.__dict__)
		self.verbose = self.debug
		if self.script is None:
			print('[e] no script specified:', self.script)
		if os.path.isfile(self.script):
			if self.verbose:
				print('[i] script specified exists:', self.script)
			self.valid = True
		else:
			print('[e] script does not exist:', self.script)
			self.valid = False
		if self.valid:
			self.make_replacements()

	def get_contents(self):
		with open(self.script, 'r') as f:
			# self.contents = [_l.strip('\n') for _l in f.readlines()]
			self.contents = f.readlines()
		return self.contents

	def get_definitions(self, _lines):
		ret_dict = {}
		s = ''.join(_lines)
		if len(s) < 1:
			return ret_dict
		if len(s) < 1:
			return ret_dict
		regex = r"[\w]+="
		matches = re.finditer(regex, s, re.MULTILINE)
		for m in matches:
			_tag = m.group(0)
			for l in _lines:
				if l[:len(_tag):] == _tag:
					ret_dict[_tag] = l[len(_tag):].strip('\n')
		return ret_dict

	def get_replacements(self, _lines):
		regex = r"{{[a-zA-Z0-9_]+}}*"
		matches = re.finditer(regex, ''.join(_lines), re.MULTILINE)
		rv_matches = []
		for m in matches:
			if m.group(0) not in rv_matches:
				rv_matches.append(m.group(0).strip('\n'))
		return rv_matches

	def replace_in_line(self, l, _definitions, _replacements):
		replaced = False
		newl = l
		for r in _replacements:
			_tag = r[2:][:-2]
			if r in newl:
				try:
					_repls = _definitions[_tag+'=']
				except KeyError:
					_repls = str(self.__getattr__(_tag))
				print('replacing', r, 'with', _repls, 'in', newl)
				newl = newl.replace(r, _repls)
				replaced = True
				print('... ->', newl)
		return newl, replaced

	def make_replacements(self):
		_contents = self.get_contents()
		_definitions = self.get_definitions(_contents)
		if self.verbose:
			print('[i] definitions:', _definitions)
		_replacements = self.get_replacements(_contents)
		if self.verbose:
			print('[i] number of replacements found', len(_replacements))
			print('   ', _replacements)
		new_contents = []
		for l in _contents:
			newl = l
			replaced = True
			while replaced:
				newl, replaced = self.replace_in_line(newl, _definitions, _replacements)
			new_contents.append(newl)
    
		for l in new_contents:
			print(l.strip('\n'))
		pass

	def exec_cmnd(self, cmnd):
		if self.verbose:
			print('[i] calling', cmnd, file=sys.stderr)
		args = shlex.split(cmnd)
		try:
			p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = p.communicate()
		except OSError as e:
			out = 'Failed.'
			err = ('Error #{0} : {1}').format(e[0], e[1])
		rc = p.returncode
		if self.verbose:
			print('    out:',out, file=sys.stderr)
			print('    err:',err, file=sys.stderr)
			print('     rc:', rc, file=sys.stderr)
		return out, err, rc

	def exec(self):
		if self.test_exec():
			self.make_replacements()
		_rv = True
		return _rv

	def test_exec(self):
		if self.verbose:
			print('[i] checking bash syntax', self.script)
		out, err, rc = self.exec_cmnd('bash -n ' + self.script)
		if rc == 0:
			return True	
		if rc > 0:
			return False
		return rc

class SoftBuild(GenericObject):
	def __init__(self, **kwargs):
		super(SoftBuild, self).__init__(**kwargs)
		if self.args:
			self.configure_from_dict(self.args.__dict__)
		self.verbose = self.debug
		if os.makedirs(self.workdir, exist_ok=True):
			os.chdir(self.workdir)

	def exec_download(self):
		os.chdir(self.workdir)
		if self.verbose:
			print('[i] current dir:', os.getcwd())
		out, err, retcode = self.exec('wget -nc {}'.format(self.download))
		if retcode > 0:
			if self.verbose:
				print('[i] returning error={}'.format(retcode))
				return retcode
     
	def main(self):
		if self.download:
			return self.exec_download()
		if self.recipe:
			return self.process_recipe()
		return 0

	def process_recipe(self):
		_rv = None
		if os.path.isfile(self.recipe):
			if self.verbose:
				print('[i] file exists:', self.recipe)
		else:
			self.recipe = os.path.join(self.recipe_dir, self.recipe, 'build.sh')
		if self.verbose:
			print('[i] processing recipe', self.recipe)
		_bs = BuildScript(script=self.recipe, args=self.args)
		if _bs.valid is False:
			_rv = False
		else:
			_rv = _bs.exec()
		return _rv

	def exec(self, cmnd):
		if self.verbose:
			print('[i] calling', cmnd, file=sys.stderr)
		args = shlex.split(cmnd)
		try:
			p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = p.communicate()
		except OSError as e:
			out = 'Failed.'
			err = ('Error #{0} : {1}').format(e[0], e[1])
		rc = p.returncode
		if self.verbose:
			print('    out:',out, file=sys.stderr)
			print('    err:',err, file=sys.stderr)
			print('     rc:', rc, file=sys.stderr)
		return out, err, rc
		

def main():
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--softbuild', help='point to softbuild.py executable - default: this script', default=__file__)
	group.add_argument('-r', '--recipe', help='name of the recipe to process', type=str)
	_recipe_dir = os.path.join(get_this_directory(), 'recipes')
	group.add_argument('--recipe-dir', help='dir where recipes info sit - default: {}'.format(_recipe_dir), default=_recipe_dir, type=str)
	group.add_argument('-d', '--download', help='download mode; needs argument that is a valid url for file', type=str)
	_default_prefix = os.path.join(get_this_directory(), 'software')
	parser.add_argument('--prefix', help='prefix of the installation {}'.format(_default_prefix), default=_default_prefix)
	parser.add_argument('-w', '--workdir', help='set the work dir for the setup - default is /tmp/softbuild', default='/tmp/softbuild', type=str)
	parser.add_argument('-g', '--debug', '--verbose', help='print some extra info', action='store_true', default=False)
	args = parser.parse_args()

	sb = SoftBuild(args=args)
	print(sb)
	return sb.main()

	# parse the build.sh and identify the parameters that could be overwritten - have to be in the form {{}}
	# replace those found in either
	# - config file
	# - in the current environment (!)
	# do not process if some variables are NOT DEFINED!

if __name__=="__main__":
	_rv = main()
	exit(_rv)
