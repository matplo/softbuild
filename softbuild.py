#!/usr/bin/env python3

import os
import argparse
import sys
import shlex
import subprocess


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


class BuildScript(GenericObject):
	_download_cmnd = os.path.join(__file__)
	def __init__(self, **kwargs):
		super(BuildScript, self).__init__(**kwargs)
		if self.args:
			self.configure_from_dict(self.args.__dict__)
		self.verbose = self.debug
  
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

	def test(self):
		out, err, rc = self.exec(self.script)
		if rc == 0:
			return True	
		if rc > 0:
			return False

class SoftBuild(GenericObject):
	def __init__(self, **kwargs):
		super(SoftBuild, self).__init__(**kwargs)
		if self.args:
			self.configure_from_dict(self.args.__dict__)
		self.verbose = self.debug
		if os.makedirs(self.workdir, exist_ok=True):
			os.chdir(self.workdir)

	def download(self):
		os.chdir(self.downloaddir)
		self.exec('wget -nc {}'.format(self.download))
     
	def main(self):
		if self.download:
			out, err, retcode = self.exec('wget -nc {}'.format(self.download))
			if retcode > 0:
				if self.verbose:
					print('[i] returning error={}'.format(retcode))
					return retcode
		return 0

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
	group.add_argument('--package', help='name of the package to build', type=str)
	group.add_argument('--download', help='download mode; needs argument that is a valid url for file', type=str)
	_default_prefix = os.path.join(get_this_directory(), 'software')
	parser.add_argument('--prefix', help='prefix of the installation {}'.format(_default_prefix), default=_default_prefix)
	parser.add_argument('--workdir', help='set the work dir for the setup', default='/tmp/softbuild', type=str)
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
